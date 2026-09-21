/**
 * Shared reactive state for SagaPT runs, powered by Svelte 5 runes.
 *
 * State lives on a single exported `$state` object so it can be mutated
 * (not reassigned) from within the module — the Svelte 5 compiler requires
 * this for exported rune state.
 */

import type {
  Run,
  RunConfig,
  Subgraph,
  AIMessagePane,
  ToolCallPane,
  SummarizerPane,
  ReflectionPane,
  RunStatus,
  PaneItem,
  TargetProfile,
} from "./types";
import * as api from "./api";

// ── Exported reactive state ───────────────────────────────────────────────────

export const store = $state({
  runs: [] as Run[],
  selectedRunId: null as string | null,
  subgraphs: [] as Subgraph[],
  /** Flat list of KB file paths, e.g. ["recon/tool_logs/get_login.md", ...] */
  kbKeys: [] as string[],
  mermaidDiagram: "",
});

// ── Private SSE state (plain module vars — not reactive) ──────────────────────

let _es: EventSource | null = null;
let _connectedId: string | null = null;
let _reconnecting = false;
let _subgraphSeq = 0;

// Global lifecycle stream — always open once connectGlobal() is called; picks
// up run_created / run_status / run_deleted events from other tabs and direct
// API callers so the run list stays live without polling.
let _globalEs: EventSource | null = null;

// ── Public API ────────────────────────────────────────────────────────────────

export async function loadRuns(): Promise<void> {
  store.runs = await api.listRuns();
}

export async function loadMermaid(): Promise<void> {
  store.mermaidDiagram = await api.getMermaid();
}

/** Select a run: disconnect any current SSE stream and connect to the new one. */
export function selectRun(id: string | null): void {
  if (id === _connectedId) return;
  _disconnect();
  store.selectedRunId = id;
  store.subgraphs = [];
  store.kbKeys = [];
  if (id !== null) _connect(id);
}

/** Create a new run using the default config against the given target profile, optional human prompt, and optional name. */
export async function createRun(target: TargetProfile, humanPrompt?: string, name?: string): Promise<void> {
  const cfg: RunConfig = await api.getDefaultConfig();
  if (humanPrompt !== undefined) cfg.planner.prompts.human = humanPrompt;
  const run = await api.createRun({
    ...cfg,
    general: { target: target.target },
    zap: target.zap,
    name: name || undefined,
  });
  // The global run_created SSE event may have already arrived and inserted
  // this run; only prepend if it hasn't.
  if (!store.runs.some((r) => r.run_id === run.run_id)) {
    store.runs = [run, ...store.runs];
  }
  selectRun(run.run_id);
}

/** Permanently delete a run (cancels first if still running). */
export async function deleteRun(id: string): Promise<void> {
  await api.deleteRun(id);
  if (store.selectedRunId === id) selectRun(null);
  store.runs = store.runs.filter((r) => r.run_id !== id);
}

/** Cancel a running or pending run without deleting it. */
export async function cancelRun(id: string): Promise<void> {
  await api.cancelRun(id);
}

/** Open the global lifecycle stream once (idempotent). */
export function connectGlobal(): void {
  if (_globalEs) return;
  _globalEs = new EventSource(`/api/v1/events`);
  _globalEs.addEventListener("run_created", (e: MessageEvent) => {
    try {
      const run = JSON.parse(e.data) as Run;
      // De-dupe: the tab that POSTed the run inserted it optimistically.
      if (store.runs.some((r) => r.run_id === run.run_id)) return;
      store.runs = [run, ...store.runs];
    } catch (err) {
      console.error("[sse:global] run_created:", err);
    }
  });
  _globalEs.addEventListener("run_status", (e: MessageEvent) => {
    try {
      const d = JSON.parse(e.data) as { run_id: string; status: RunStatus; error?: string };
      const idx = store.runs.findIndex((r) => r.run_id === d.run_id);
      if (idx !== -1) {
        store.runs[idx] = { ...store.runs[idx], status: d.status, error: d.error };
      }
    } catch (err) {
      console.error("[sse:global] run_status:", err);
    }
  });
  _globalEs.addEventListener("run_deleted", (e: MessageEvent) => {
    try {
      const d = JSON.parse(e.data) as { run_id: string };
      if (store.selectedRunId === d.run_id) selectRun(null);
      store.runs = store.runs.filter((r) => r.run_id !== d.run_id);
    } catch (err) {
      console.error("[sse:global] run_deleted:", err);
    }
  });
}

/** Close every active SSE connection (call from onDestroy). */
export function cleanup(): void {
  _disconnect();
  if (_globalEs) {
    _globalEs.close();
    _globalEs = null;
  }
}

// ── SSE connection lifecycle ──────────────────────────────────────────────────

function _connect(runId: string): void {
  _connectedId = runId;
  _es = new EventSource(`/api/v1/runs/${runId}/events`);

  _es.onerror = () => {
    _reconnecting = true;
  };

  // On reconnect the backend replays all stored events — reset derived state
  // first to avoid duplicating panes.
  _es.onopen = () => {
    if (_reconnecting) {
      store.subgraphs = [];
      store.kbKeys = [];
      _reconnecting = false;
    }
  };

  const on = (type: string, fn: (d: unknown) => void) =>
    _es!.addEventListener(type, (e: MessageEvent) => {
      try {
        fn(JSON.parse(e.data));
      } catch (err) {
        console.error(`[sse] failed to handle ${type}:`, err);
      }
    });

  on("run_status", _onRunStatus);
  on("planner_message", _onPlannerMessage);
  on("subgraph_start", _onSubgraphStart);
  on("subgraph_agent_message", _onSubgraphAgentMessage);
  on("subgraph_reflection", _onSubgraphReflection);
  on("subgraph_tool_call", _onSubgraphToolCall);
  on("subgraph_kb_tool_call", _onSubgraphKbToolCall);
  on("planner_kb_tool_call", _onPlannerKbToolCall);
  on("subgraph_message", _onSubgraphMessage);
  on("subgraph_end", _onSubgraphEnd);
  on("kb_update", _onKbUpdate);
  on("token", _onToken);
  on("error", _onSseError);
}

function _disconnect(): void {
  if (_es) {
    _es.close();
    _es = null;
  }
  _connectedId = null;
}

// ── SSE event handlers ────────────────────────────────────────────────────────

interface RunStatusPayload {
  run_id: string;
  status: RunStatus;
  error?: string;
}

function _onRunStatus(data: unknown): void {
  const d = data as RunStatusPayload;
  const idx = store.runs.findIndex((r) => r.run_id === d.run_id);
  if (idx !== -1) store.runs[idx] = { ...store.runs[idx], status: d.status, error: d.error };
  const terminal = d.status === "completed" || d.status === "failed" || d.status === "cancelled";
  if (terminal) _disconnect();
}

interface PlannerMessagePayload {
  run_id: string;
  reasoning?: string;
  content: string;
  tool_calls: Array<{
    agent: string;
    instructions: string;
    execution_name?: string;
    /** Raw tool-call args — populated for every kind (agent dispatch or kb_get/kb_list_dir). */
    args?: Record<string, unknown>;
  }>;
}

function _onPlannerMessage(data: unknown): void {
  const d = data as PlannerMessagePayload;
  const pane: AIMessagePane = {
    type: "ai",
    node: "planner",
    reasoning: d.reasoning ?? undefined,
    content: d.content,
    // Map planner tool_calls → ToolCallRef {name, args}. `args` carries the raw
    // tool-call arguments so KB reads (kb_get/kb_list_dir) render their actual
    // args instead of the dispatch-only instructions/execution_name fields.
    tool_calls: d.tool_calls.map((tc) => ({
      name: tc.agent,
      args: tc.args ?? { instructions: tc.instructions, execution_name: tc.execution_name },
    })),
  };
  // Token events for the planner stream into the most recent planner subgraph
  // before this message event arrives. Remove any trailing token placeholder
  // (AI pane with no tool_calls) to avoid showing the content twice.
  const prev = _lastSubgraph("planner");
  if (prev) {
    const last = prev.panes[prev.panes.length - 1];
    if (last?.type === "ai" && !(last as AIMessagePane).tool_calls?.length) {
      prev.panes = prev.panes.slice(0, -1);
    }
  }
  store.subgraphs = [
    ...store.subgraphs,
    { id: ++_subgraphSeq, agent: "planner", execution_name: "", instructions: "", status: "running", panes: [pane] },
  ];
}

interface SubgraphStartPayload {
  run_id: string;
  agent: string;
  execution_name: string;
  instructions: string;
}

function _onSubgraphStart(data: unknown): void {
  const d = data as SubgraphStartPayload;
  store.subgraphs = [
    ...store.subgraphs,
    { id: ++_subgraphSeq, agent: d.agent, execution_name: d.execution_name, instructions: d.instructions, status: "running", panes: [] },
  ];
}

interface SubgraphAgentMessagePayload {
  run_id: string;
  agent: string;
  node: string;
  reasoning?: string;
  content: string;
  tool_calls: Array<{ tool: string; args: Record<string, unknown> }>;
}

function _onSubgraphAgentMessage(data: unknown): void {
  const d = data as SubgraphAgentMessagePayload;
  const pane: AIMessagePane = {
    type: "ai",
    node: d.node,
    reasoning: d.reasoning ?? undefined,
    content: d.content,
    // Map agent tool_calls {tool, args} → ToolCallRef {name, args}
    tool_calls: d.tool_calls.map((tc) => ({ name: tc.tool, args: tc.args })),
  };
  const sg = _lastSubgraph(d.agent);
  if (!sg) return;
  const last = sg.panes[sg.panes.length - 1];
  // Replace a token-streaming placeholder (AI pane with no tool_calls) with the
  // complete message; otherwise append.
  if (last?.type === "ai" && !(last as AIMessagePane).tool_calls?.length) {
    sg.panes[sg.panes.length - 1] = pane;
  } else {
    sg.panes = [...sg.panes, pane];
  }
}

interface SubgraphReflectionPayload {
  run_id: string;
  agent: string;
  reasoning?: string;
  content: string;
}

function _onSubgraphReflection(data: unknown): void {
  const d = data as SubgraphReflectionPayload;
  const pane: ReflectionPane = {
    type: "reflection",
    reasoning: d.reasoning ?? undefined,
    content: d.content,
  };
  const sg = _lastSubgraph(d.agent);
  if (!sg) return;
  const last = sg.panes[sg.panes.length - 1];
  // Replace a token-streaming placeholder (AI pane with no tool_calls) with the
  // completed reflection; otherwise append.
  if (last?.type === "ai" && !(last as AIMessagePane).tool_calls?.length) {
    sg.panes[sg.panes.length - 1] = pane;
  } else {
    sg.panes = [...sg.panes, pane];
  }
}

interface SubgraphToolCallPayload {
  run_id: string;
  agent: string;
  execution_name?: string;
  tool_name: string;
  tool_args: Record<string, unknown>;
  raw_output: string;
  kb_key: string;
  summary: string | null;
}

function _onSubgraphToolCall(data: unknown): void {
  const d = data as SubgraphToolCallPayload;
  // Remove any stale AI streaming placeholder (e.g. leaked summarizer tokens)
  // before appending the tool result panes.
  const sgForCleanup = _lastSubgraph(d.agent);
  if (sgForCleanup) {
    const last = sgForCleanup.panes[sgForCleanup.panes.length - 1];
    if (last?.type === "ai" && !(last as AIMessagePane).tool_calls?.length) {
      sgForCleanup.panes = sgForCleanup.panes.slice(0, -1);
    }
  }
  const toolPane: ToolCallPane = {
    type: "tool_call",
    tool_name: d.tool_name,
    args: d.tool_args,
    result: d.raw_output,
  };
  _appendPane(d.agent, toolPane);
  // summary is null when the tool result skipped summarization — nothing to render.
  if (d.summary) {
    const summaryPane: SummarizerPane = {
      type: "summarizer",
      kb_key: d.kb_key,
      summary: d.summary,
    };
    _appendPane(d.agent, summaryPane);
  }
}

interface SubgraphKbToolCallPayload {
  run_id: string;
  agent: string;
  tool_name: string;
  tool_args: Record<string, unknown>;
  result: string;
}

function _onSubgraphKbToolCall(data: unknown): void {
  const d = data as SubgraphKbToolCallPayload;
  const pane: ToolCallPane = {
    type: "tool_call",
    tool_name: d.tool_name,
    args: d.tool_args,
    result: d.result,
  };
  _appendPane(d.agent, pane);
}

interface PlannerKbToolCallPayload {
  run_id: string;
  tool_name: string;
  tool_args: Record<string, unknown>;
  result: string;
}

function _onPlannerKbToolCall(data: unknown): void {
  const d = data as PlannerKbToolCallPayload;
  const pane: ToolCallPane = {
    type: "tool_call",
    tool_name: d.tool_name,
    args: d.tool_args,
    result: d.result,
  };
  _appendPane("planner", pane);
}

interface SubgraphEndPayload {
  run_id: string;
  agent: string;
  execution_name?: string;
  result: string;
}

interface SubgraphMessagePayload {
  run_id: string;
  agent: string;
  role: "system" | "human";
  content: string;
}

function _onSubgraphMessage(data: unknown): void {
  const d = data as SubgraphMessagePayload;
  const pane: PaneItem = { type: "message", role: d.role, content: d.content };
  // Auto-create a setup subgraph if none exists yet (e.g. planner init messages
  // arrive before the first planner_message creates a subgraph).
  if (!_lastSubgraph(d.agent)) {
    store.subgraphs = [
      ...store.subgraphs,
      { id: ++_subgraphSeq, agent: d.agent, execution_name: "", instructions: "", status: "running", panes: [pane] },
    ];
  } else {
    _appendPane(d.agent, pane);
  }
}

function _onSubgraphEnd(data: unknown): void {
  const d = data as SubgraphEndPayload;
  const sg = _lastSubgraph(d.agent);
  if (sg) sg.status = "completed";
}

interface KbUpdatePayload {
  run_id: string;
  keys: string[];
}

function _onKbUpdate(data: unknown): void {
  const d = data as KbUpdatePayload;
  // Just record the key paths — file contents are loaded lazily by the KB panel.
  store.kbKeys = d.keys;
}

interface TokenPayload {
  run_id: string;
  agent: string;
  node: string;
  token: string;
}

function _onToken(data: unknown): void {
  const d = data as TokenPayload;
  // Summarizer tokens are shown via SummarizerPane — skip streaming placeholders.
  if (d.node === "summarize") return;
  const sg = _lastSubgraph(d.agent);
  if (!sg) return;
  const last = sg.panes[sg.panes.length - 1];
  if (last?.type === "ai" && !(last as AIMessagePane).tool_calls?.length) {
    // Append to existing streaming placeholder.
    (last as AIMessagePane).content = ((last as AIMessagePane).content ?? "") + d.token;
  } else {
    // Create a new streaming placeholder.
    sg.panes = [...sg.panes, { type: "ai", content: d.token } as AIMessagePane];
  }
}

function _onSseError(data: unknown): void {
  const d = data as { run_id: string; message: string };
  console.error(`[sse] run ${d.run_id} error:`, d.message);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function _lastSubgraph(agent: string): Subgraph | null {
  for (let i = store.subgraphs.length - 1; i >= 0; i--) {
    if (store.subgraphs[i].agent === agent) return store.subgraphs[i];
  }
  return null;
}

function _appendPane(agent: string, pane: PaneItem): void {
  const sg = _lastSubgraph(agent);
  if (sg) sg.panes = [...sg.panes, pane];
}
