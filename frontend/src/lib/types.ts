export type Align = "left" | "right";

/** A system or human message in the agent's message history. */
export interface MessagePane {
  type: "message";
  role: "system" | "human";
  content: string;
  align?: Align;
}

/** A single tool call within an AI message. */
export interface ToolCallRef {
  name: string;
  args: Record<string, unknown>;
}

/** An AI/LLM response with optional reasoning, content, and tool calls. */
export interface AIMessagePane {
  type: "ai";
  /** LangGraph node name, e.g. "agent" or "planner". */
  node?: string;
  reasoning?: string;
  content?: string;
  tool_calls?: ToolCallRef[];
  align?: Align;
}

/** The result of a single tool execution (args + raw result). */
export interface ToolCallPane {
  type: "tool_call";
  tool_name: string;
  args: Record<string, unknown>;
  result?: string;
  align?: Align;
}

/** The summarizer's condensed write-up of a tool result, stored in the KB. */
export interface SummarizerPane {
  type: "summarizer";
  kb_key: string;
  summary: string;
  align?: Align;
}

/** A forced tool-less checkpoint turn where the agent justifies its approach. */
export interface ReflectionPane {
  type: "reflection";
  reasoning?: string;
  content?: string;
  align?: Align;
}

export type PaneItem = MessagePane | AIMessagePane | ToolCallPane | SummarizerPane | ReflectionPane;

export type RunStatus = "pending" | "running" | "completed" | "failed" | "cancelled";

/** All data needed to render a single agent subgraph. */
export interface Subgraph {
  /** Auto-incrementing id for stable {#each} keying. */
  id: number;
  agent: string;
  execution_name: string;
  instructions: string;
  status: RunStatus;
  panes: PaneItem[];
  align?: Align;
}

/** A run as returned by the API (mirrors RunSummary in api.py). */
export interface Run {
  run_id: string;
  name: string;
  status: RunStatus;
  target: string;
  /** ISO-8601 datetime string from Pydantic serialisation. */
  started_at: string;
  ended_at?: string;
  error?: string;
}

/** A single knowledge base entry. */
export interface KBEntry {
  key: string;
  value: string;
}

// ── RunConfig mirrors the RunConfig Pydantic model in api.py ─────────────────

interface _PromptsConfig { system: string; human: string; }
interface _ModelConfig { model_provider: string; model_name: string; temperature: number; model_kwargs?: Record<string, unknown>; }
interface _AgentRunConfig extends _ModelConfig { name: string; description: string; tools: string[]; prompts: _PromptsConfig; reflection_interval?: number; max_tool_calls?: number; }
interface _SummarizerRunConfig extends _ModelConfig { prompts: _PromptsConfig; }
interface _PlannerRunConfig extends _ModelConfig { prompts: _PromptsConfig; }

export interface ZapRunConfig {
  context_name?: string;
  include: string[];
  exclude: string[];
  spider_exclude: string[];
}

export interface RunConfig {
  general: { target: string };
  summarizer: _SummarizerRunConfig;
  planner: _PlannerRunConfig;
  agents: Record<string, _AgentRunConfig>;
  zap?: ZapRunConfig;
  name?: string;
}

/** A named, selectable target (mirrors a `[targets.<key>]` table in saga.toml). */
export interface TargetProfile {
  key: string;
  label: string;
  target: string;
  zap: ZapRunConfig;
  human_prompt: string | null;
}
