"""Run lifecycle management and SSE broadcast fan-out for SagaPT.

This module is intentionally free of FastAPI concerns so it can be imported
and tested independently. ``api.py`` depends on this module; this module
depends only on ``runner.py`` and ``knowledge_base.py``.
"""

import asyncio
import json
import logging
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import CompiledStateGraph
from sse_starlette.sse import ServerSentEvent

from graph.message_content import extract_text
from graph.subgraph import _make_slug
from knowledge_base import KnowledgeBase, slugify
from report_parser import ReportFinding, parse_findings_table
from runner import dict_to_tuple_list

logger = logging.getLogger(__name__)

_RAW_OUTPUT_MAX = 2_000
_NAME_RE = re.compile(r"^Run #(\d+)$")


def _make_run_id(dt: datetime, seq: int) -> str:
    """Build a human-readable, URL/filename-safe run ID from a datetime and sequence number.

    Example: ``_make_run_id(dt, 3)`` → ``"20260515-0848-0003"``
    """
    return dt.strftime("%Y%m%d-%H%M") + f"-{seq:04d}"


class RunStatus(str, Enum):
    """Lifecycle status of a single graph run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


TERMINAL_STATUSES: frozenset[RunStatus] = frozenset(
    [RunStatus.COMPLETED, RunStatus.CANCELLED, RunStatus.FAILED]
)


class StoredEvent(TypedDict):
    """A semantic SSE event stored for history replay and client reconnect.

    Token events are intentionally excluded — they are too numerous to store
    and can be reconstructed from the complete message events.
    """

    type: str
    payload: dict
    ts: str  # ISO-8601 UTC timestamp


@dataclass
class RunState:
    """All mutable state associated with one graph execution."""

    run_id: str
    name: str
    status: RunStatus
    target: str
    started_at: datetime
    ended_at: datetime | None
    kb: KnowledgeBase | None
    error: str | None = None
    # Per-agent config snapshot at run start (keyed by graph-node name, e.g.
    # "recon_agent") — max_tool_calls/reflection_interval/model_name. Lets the
    # CSV export detect hard-cap hits without re-reading (possibly since
    # changed) config. Populated by api.py's create_run(); empty for runs
    # started before this field existed.
    agent_config: dict[str, dict] = field(default_factory=dict, repr=False)
    # Findings parsed from the planner's final report (see report_parser.py).
    findings: list[ReportFinding] = field(default_factory=list, repr=False)
    # Running total of tokens consumed across every AI event in this run.
    # Updated by stream_run() at each _extract_usage() call site; also
    # compared against the run's token_budget (if set) to enforce a cap.
    total_tokens: int = 0
    # Semantic events stored for reconnect / history replay (no token events).
    stored_events: list[StoredEvent] = field(default_factory=list, repr=False)
    # Set after persist_run(); used to load events from disk when evicted.
    events_file: Path | None = field(default=None, repr=False)
    # Each SSE client subscribes with its own asyncio.Queue.
    # None is the end-of-stream sentinel.
    _subscribers: list[asyncio.Queue] = field(default_factory=list, repr=False)
    _task: asyncio.Task | None = field(default=None, repr=False)


class TokenBudgetExceeded(Exception):
    """Raised inside ``stream_run`` when a run's total tokens surpass its budget.

    Caught in ``api.py::_build_and_stream``'s existing ``except Exception``
    handler and translated into a ``FAILED`` terminal state with a clear
    error message. Deliberately a distinct type so callers can pattern-match
    on it (e.g. XBOW harness maps it to ``budget_hit: "token_budget"``).
    """

    def __init__(self, total: int, budget: int) -> None:
        self.total = total
        self.budget = budget
        super().__init__(f"Token budget exceeded: {total} / {budget} tokens")


# ---------------------------------------------------------------------------
# LangGraph event helpers
# ---------------------------------------------------------------------------


def _extract_agent(checkpoint_ns: str) -> str:
    """Extract agent name from LangGraph checkpoint namespace.

    Examples:
        ``"recon:abc123"`` → ``"recon"``
        ``""``             → ``"planner"``
    """
    if not checkpoint_ns:
        return "planner"
    return checkpoint_ns.split(":")[0]


def _extract_reasoning(ai_message: AIMessage) -> str | None:
    """Extract reasoning/thinking content from an AIMessage, or None.

    Handles the provider conventions Saga sees:
    - Groq / DeepSeek: ``additional_kwargs["reasoning_content"]``
    - Anthropic extended thinking + Gemini (default output_version): content
      list blocks with ``type == "thinking"`` (text under the ``"thinking"`` key)
    - Gemini via langchain-core v1 ``ReasoningContentBlock``: content list
      blocks with ``type == "reasoning"`` (text under the ``"reasoning"`` key)
    - Standard models: no reasoning content → returns None

    Note: Gemini only *returns* thought summaries as content blocks when the
    model is built with ``include_thoughts=True``; without it, reasoning is
    counted in ``usage.reasoning_tokens`` but never emitted as content, so
    this correctly returns None even though the turn "thought".
    """
    reasoning = ai_message.additional_kwargs.get("reasoning_content")
    if reasoning:
        return str(reasoning)
    content = ai_message.content
    if isinstance(content, list):
        # Two block shapes carry reasoning text depending on output_version:
        # {"type": "thinking", "thinking": ...} and {"type": "reasoning", "reasoning": ...}.
        parts = [
            block[block["type"]]
            for block in content
            if isinstance(block, dict)
            and block.get("type") in ("thinking", "reasoning")
            and block.get(block["type"])
        ]
        if parts:
            return "\n".join(parts)
    return None


def _extract_content(ai_message: AIMessage) -> str:
    """Extract plain text content from an AIMessage.

    Delegates to :func:`graph.message_content.extract_text` so the SSE content
    shown in the trace and the agent/planner nudge's emptiness guard always
    agree on what counts as "text" — a divergence here is exactly what let a
    textless Gemini-3 reasoning turn slip past the nudge.
    """
    return extract_text(ai_message.content)


def _account_usage(
    run_state: "RunState",
    usage: dict | None,
    token_budget: int | None,
) -> None:
    """Add usage tokens to the run's running total and enforce the token budget.

    Called at every ``_extract_usage`` site inside ``stream_run``. Raises
    :class:`TokenBudgetExceeded` when the cumulative total crosses the
    budget — the exception propagates into stream_run's ``except Exception``
    branch, which sets FAILED status with a clear error message.
    """
    if not usage:
        return
    total = usage.get("total_tokens") or 0
    if not total:
        return
    run_state.total_tokens += total
    if token_budget is not None and token_budget > 0 and run_state.total_tokens > token_budget:
        raise TokenBudgetExceeded(run_state.total_tokens, token_budget)


def _extract_usage(ai_message: AIMessage) -> dict | None:
    """Extract token usage + model name from an AIMessage, or None if absent.

    Handles two response shapes:

    1. **Google / Ollama** (standard LangChain): ``usage_metadata`` carries
       ``input_tokens``/``output_tokens``/``total_tokens`` plus an
       ``input_token_details.cache_read`` breakdown; ``response_metadata``
       carries ``model_name``.

    2. **OpenAI-compatible** (``llamacpp`` via ``ChatOpenAI``): ``response_metadata``
       carries ``model`` (not ``model_name``) and ``usage`` with
       ``prompt_tokens``/``completion_tokens``/``total_tokens`` — the OpenAI
       naming convention. ``usage_metadata`` may be absent when the provider
       doesn't emit it in the streaming chunks.
    """
    # --- model name ---
    model_name = (
        ai_message.response_metadata.get("model_name")
        or ai_message.response_metadata.get("model")
    )

    # --- token usage: standard LangChain path (Google, Ollama) ---
    usage = ai_message.usage_metadata
    if usage:
        input_details = usage.get("input_token_details") or {}
        output_details = usage.get("output_token_details") or {}
        return {
            "model_name": model_name,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "cached_input_tokens": input_details.get("cache_read", 0),
            "reasoning_tokens": output_details.get("reasoning", 0),
        }

    # --- fallback: OpenAI-compatible ``response_metadata["usage"]`` ---
    raw_usage = ai_message.response_metadata.get("usage")
    if raw_usage:
        if isinstance(raw_usage, dict):
            return {
                "model_name": model_name,
                "input_tokens": raw_usage.get("prompt_tokens", 0),
                "output_tokens": raw_usage.get("completion_tokens", 0),
                "total_tokens": raw_usage.get("total_tokens", 0),
                "cached_input_tokens": 0,
                "reasoning_tokens": 0,
            }
        # Some providers return a ``Usage`` dataclass; try the standard attrs.
        return {
            "model_name": model_name,
            "input_tokens": getattr(raw_usage, "prompt_tokens", 0),
            "output_tokens": getattr(raw_usage, "completion_tokens", 0),
            "total_tokens": getattr(raw_usage, "total_tokens", 0),
            "cached_input_tokens": 0,
            "reasoning_tokens": 0,
        }

    return None


def _is_top_level_node(event: dict, node: str) -> bool:
    """Return True only for top-level LangGraph node chain events.

    LangGraph fires ``on_chain_start/end`` for every Runnable invocation inside
    a node (prompt templates, output parsers, LCEL sub-chains) with the same
    ``langgraph_node`` metadata as the enclosing node. For the actual node-level
    event, ``event["name"]`` matches the registered node name.
    """
    return event.get("name") == node


# ---------------------------------------------------------------------------
# Stream context (state machine helpers for stream_run)
# ---------------------------------------------------------------------------


@dataclass
class _PendingToolCall:
    """Buffer for a ZAP tool call awaiting its summarizer result."""

    agent: str
    tool_name: str
    tool_args: dict
    raw_output: dict | None = None
    kb_key: str | None = None
    """Agent-provided KB key from the tool's JSON output; overrides auto-generation."""
    execution_name: str | None = None
    """Planner-provided label for the invocation that produced this tool call."""


@dataclass
class _StreamCtx:
    """Mutable context for one ``stream_run()`` invocation."""

    agent_names: frozenset[str]
    # agent_name → instructions string; populated from planner tool calls
    # and consumed when the matching subgraph node starts.
    pending_instructions: dict[str, str] = field(default_factory=dict)
    # agent_name → execution_name string; same lifecycle as pending_instructions.
    pending_execution_names: dict[str, str] = field(default_factory=dict)
    # Maps checkpoint_ns → ordered list of _PendingToolCall items read from
    # the summarize node's input state (pending_tool_results).  Each
    # on_chat_model_end inside summarize pops the first entry.
    pending_summarize: dict[str, list[_PendingToolCall]] = field(default_factory=dict)
    prev_kb_keys: list[str] = field(default_factory=list)
    # Agent names for which initial system/human messages have already been emitted.
    # Keyed by agent name (not checkpoint ns) so re-invocations after tool calls don't re-emit.
    emitted_init_messages: set[str] = field(default_factory=set)
    # checkpoint_ns → count of on_chat_model_error events seen for the "agent"
    # node in that ns — i.e. _invoke_agent_llm's transient parse-failure
    # retries. Popped and attached to the next successful subgraph_agent_message.
    pending_retry_counts: dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# RunManager
# ---------------------------------------------------------------------------


class RunManager:
    """In-memory store for all runs and SSE broadcast logic."""

    def __init__(self) -> None:
        self._runs: dict[str, RunState] = {}
        self._run_counter: int = 0
        # Subscribers to the global lifecycle stream (run_created / run_status /
        # run_deleted). Separate from per-run queues so other tabs / external
        # API callers see new runs appear without polling.
        self._global_subscribers: list[asyncio.Queue] = []

    def next_run_id_and_name(self) -> tuple[str, str]:
        """Allocate the next run ID and default name.

        Increments the internal counter and returns a ``(run_id, name)`` pair
        where ``run_id`` is filename/URL-safe and ``name`` is human-readable.
        """
        self._run_counter += 1
        run_id = _make_run_id(datetime.now(timezone.utc), self._run_counter)
        name = f"Run #{self._run_counter}"
        return run_id, name

    def create_run(
        self, run_id: str, name: str, kb: KnowledgeBase | None, target: str
    ) -> RunState:
        """Create and register a new run in PENDING state."""
        state = RunState(
            run_id=run_id,
            name=name,
            status=RunStatus.PENDING,
            target=target,
            started_at=datetime.now(timezone.utc),
            ended_at=None,
            kb=kb,
        )
        self._runs[run_id] = state
        return state

    def get_run(self, run_id: str) -> RunState | None:
        """Return the RunState for ``run_id``, or None if not found."""
        return self._runs.get(run_id)

    def list_runs(self) -> list[RunState]:
        """Return all runs sorted most-recent first."""
        return sorted(self._runs.values(), key=lambda r: r.started_at, reverse=True)

    def subscribe(self, run_id: str) -> asyncio.Queue:
        """Create and register a new subscriber queue for ``run_id``.

        Each SSE client call creates its own queue. Events are broadcast to all
        registered queues. The caller must call :meth:`unsubscribe` when done.
        """
        q: asyncio.Queue[ServerSentEvent | None] = asyncio.Queue(maxsize=512)
        run = self._runs[run_id]
        run._subscribers.append(q)
        return q

    def unsubscribe(self, run_id: str, q: asyncio.Queue) -> None:
        """Remove a subscriber queue, silently ignoring unknown runs/queues."""
        run = self._runs.get(run_id)
        if run is None:
            return
        try:
            run._subscribers.remove(q)
        except ValueError:
            pass

    def broadcast(
        self,
        run_id: str,
        event_type: str,
        payload: dict[str, Any],
        *,
        store: bool = True,
    ) -> None:
        """Serialize ``payload`` as JSON and broadcast to all subscriber queues.

        If ``store`` is True (the default), the event is also appended to
        ``RunState.stored_events`` for reconnecting clients and history replay.
        Pass ``store=False`` for token events, which are too numerous to store.

        Slow clients whose queues are full are silently skipped (drop strategy).
        """
        run = self._runs.get(run_id)
        if run is None:
            return
        if store:
            run.stored_events.append(
                StoredEvent(
                    type=event_type,
                    payload=payload,
                    ts=datetime.now(timezone.utc).isoformat(),
                )
            )
        sse = ServerSentEvent(data=json.dumps(payload), event=event_type)
        for q in list(run._subscribers):
            try:
                q.put_nowait(sse)
            except asyncio.QueueFull:
                logger.debug("Dropped SSE event for slow subscriber on run %s.", run_id)

    def global_subscribe(self) -> asyncio.Queue:
        """Subscribe to the global lifecycle stream (run_created/status/deleted).

        Each SSE client on ``/api/v1/events`` gets its own queue. The caller
        must call :meth:`global_unsubscribe` when done.
        """
        q: asyncio.Queue[ServerSentEvent | None] = asyncio.Queue(maxsize=512)
        self._global_subscribers.append(q)
        return q

    def global_unsubscribe(self, q: asyncio.Queue) -> None:
        """Remove a global subscriber queue, silently ignoring unknown queues."""
        try:
            self._global_subscribers.remove(q)
        except ValueError:
            pass

    def broadcast_global(self, event_type: str, payload: dict[str, Any]) -> None:
        """Broadcast a lifecycle event to every global subscriber.

        Used for run_created / run_status / run_deleted so other tabs see new
        runs and status changes without polling. Slow clients whose queues are
        full are silently skipped (drop strategy), matching per-run behaviour.
        """
        sse = ServerSentEvent(data=json.dumps(payload), event=event_type)
        for q in list(self._global_subscribers):
            try:
                q.put_nowait(sse)
            except asyncio.QueueFull:
                logger.debug("Dropped global SSE event %s for slow subscriber.", event_type)

    def close_broadcast(self, run_id: str) -> None:
        """Send the end-of-stream sentinel (None) to all subscriber queues."""
        run = self._runs.get(run_id)
        if run is None:
            return
        for q in list(run._subscribers):
            try:
                q.put_nowait(None)
            except asyncio.QueueFull:
                pass

    def load_run_events(self, run_id: str) -> list[StoredEvent]:
        """Return stored events for a run, loading from disk if evicted from memory.

        Raises ``KeyError`` if the run is unknown entirely.
        """
        run = self._runs.get(run_id)
        if run is None:
            raise KeyError(run_id)
        if run.stored_events:
            return list(run.stored_events)
        if run.events_file is not None and run.events_file.exists():
            data = json.loads(run.events_file.read_text(encoding="utf-8"))
            return [
                StoredEvent(type=ev["type"], payload=ev["payload"], ts=ev["ts"])
                for ev in data.get("events", [])
            ]
        return []

    def persist_run(self, run_id: str, runs_dir: Path) -> None:
        """Serialize a finished run to disk and release in-memory event storage.

        Writes ``{runs_dir}/{run_id}/trace.json``.  The KB is already on disk
        at ``{runs_dir}/{run_id}/knowledge_base.json`` via write-through, so
        only the trace needs to be written here.

        The run stub (metadata + ``events_file`` pointer) stays in ``_runs``
        so list/status endpoints keep working. Only ``stored_events`` is cleared
        to reclaim RAM, and the ``kb`` reference is dropped.
        """
        run = self._runs.get(run_id)
        if run is None:
            return
        run_dir = runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        file_path = run_dir / "trace.json"
        payload: dict[str, Any] = {
            "run_id": run.run_id,
            "name": run.name,
            "status": run.status,
            "target": run.target,
            "started_at": run.started_at.isoformat(),
            "ended_at": run.ended_at.isoformat() if run.ended_at else None,
            "error": run.error,
            "agent_config": run.agent_config,
            "findings": run.findings,
            "total_tokens": run.total_tokens,
            "events": list(run.stored_events),
        }
        file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Run %s persisted to %s.", run_id, file_path)
        run.events_file = file_path
        run.stored_events.clear()
        run.kb = None

    def delete_run(self, run_id: str, runs_dir: Path) -> None:
        """Cancel if running, evict from memory, and delete files from disk.

        Safe to call on runs in any state. The run directory is validated
        against ``runs_dir`` before deletion to prevent path traversal.
        """
        run = self._runs.get(run_id)
        if run is None:
            return
        if run._task and not run._task.done():
            run._task.cancel()
        self.close_broadcast(run_id)
        del self._runs[run_id]
        run_dir = (runs_dir / run_id).resolve()
        try:
            run_dir.relative_to(runs_dir.resolve())
        except ValueError:
            logger.error("Refusing to delete run dir outside runs_dir: %s", run_dir)
            return
        if run_dir.exists():
            shutil.rmtree(run_dir)
            logger.info("Deleted run directory %s.", run_dir)

    def load_persisted_runs(self, runs_dir: Path) -> None:
        """Scan ``runs_dir`` and register lightweight stubs for all saved runs.

        Looks for ``{runs_dir}/*/trace.json`` — one subdirectory per run.
        Called once on API startup so list/status endpoints reflect history
        across server restarts. Events are loaded lazily from disk on demand.
        """
        if not runs_dir.exists():
            return
        count = 0
        for file_path in sorted(runs_dir.glob("*/trace.json")):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
                run_id = data["run_id"]
                if run_id in self._runs:
                    continue
                started_at = datetime.fromisoformat(data["started_at"])
                ended_at = (
                    datetime.fromisoformat(data["ended_at"])
                    if data.get("ended_at")
                    else None
                )
                stub = RunState(
                    run_id=run_id,
                    name=data.get("name", run_id[:8]),
                    status=RunStatus(data["status"]),
                    target=data.get("target", ""),
                    started_at=started_at,
                    ended_at=ended_at,
                    kb=None,
                    error=data.get("error"),
                    agent_config=data.get("agent_config", {}),
                    findings=data.get("findings", []),
                    total_tokens=data.get("total_tokens", 0),
                    events_file=file_path,
                )
                self._runs[run_id] = stub
                count += 1
            except Exception as exc:
                logger.warning(
                    "Failed to load persisted run from %s: %s", file_path, exc
                )
        # Restore the counter so new run numbers continue from the highest seen value.
        for run_state in self._runs.values():
            m = _NAME_RE.match(run_state.name)
            if m:
                self._run_counter = max(self._run_counter, int(m.group(1)))
        if count:
            logger.info("Loaded %d persisted run(s) from %s.", count, runs_dir)


# ---------------------------------------------------------------------------
# stream_run
# ---------------------------------------------------------------------------


async def stream_run(
    run_state: RunState,
    graph: CompiledStateGraph,
    initial_state: dict[str, Any],
    agent_names: frozenset[str],
    runs_dir: Path,
    token_budget: int | None = None,
) -> None:
    """Background task that drives the graph and broadcasts SSE events.

    Translates fine-grained LangGraph ``astream_events`` output into semantic
    SSE events and maintains a ``stored_events`` list for history replay.
    Token events are broadcast live but not stored (too numerous for replay).

    Transitions ``run_state.status`` through RUNNING → COMPLETED/FAILED/CANCELLED,
    persists the run to ``runs_dir``, and signals ``close_broadcast()`` on exit
    so every subscriber receives the end-of-stream sentinel.

    Args:
        token_budget: If set (>0), abort the run with FAILED status once the
            cumulative token count across all AI events exceeds this value.
            ``None`` or ``<=0`` means unlimited. Wall-clock budget is
            enforced by the caller (``asyncio.wait_for`` in ``api.py``).
    """
    run_id = run_state.run_id
    run_state.status = RunStatus.RUNNING
    _status_payload = {
        "run_id": run_id,
        "status": run_state.status,
        "error": None,
    }
    run_manager.broadcast(run_id, "run_status", _status_payload)
    run_manager.broadcast_global("run_status", _status_payload)

    ctx = _StreamCtx(agent_names=agent_names)

    final_report: str = ""

    # Saved so the finally block can explicitly close it on failure paths.
    _event_stream = graph.astream_events(
        initial_state,
        {"recursion_limit": 200},
        version="v2",
        subgraphs=True,
    )
    try:
        async for event in _event_stream:
            kind: str = event["event"]
            metadata: dict = event.get("metadata", {})
            ns: str = metadata.get("langgraph_checkpoint_ns", "")
            node: str = metadata.get("langgraph_node", "")
            agent = _extract_agent(ns)

            # ------------------------------------------------------------------
            # Token streaming — live only, not stored
            # ------------------------------------------------------------------
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                content = chunk.content
                if isinstance(content, list):
                    token = "".join(
                        c.get("text", "") if isinstance(c, dict) else str(c)
                        for c in content
                    )
                else:
                    token = str(content)
                if token:
                    run_manager.broadcast(
                        run_id,
                        "token",
                        {
                            "run_id": run_id,
                            "agent": agent,
                            "node": node,
                            "token": token,
                        },
                        store=False,
                    )

            # ------------------------------------------------------------------
            # KB tool execution (via ToolNode) — ZAP tools bypass LangGraph's
            # tool dispatch so on_tool_end only fires for KB tools. Subgraph-level
            # calls (ns contains "|") are agent KB reads/writes; top-level calls
            # (ns == "") are the planner's read-only kb_get/kb_list_dir.
            # ------------------------------------------------------------------
            elif kind == "on_tool_end" and "|" in ns:
                tool_name = event.get("name", "")
                tool_input = event["data"].get("input") or {}
                result = str(event["data"].get("output") or "")
                run_manager.broadcast(
                    run_id,
                    "subgraph_kb_tool_call",
                    {
                        "run_id": run_id,
                        "agent": agent,
                        "tool_name": tool_name,
                        "tool_args": tool_input,
                        "result": result,
                    },
                )

            elif kind == "on_tool_end" and "|" not in ns:
                tool_name = event.get("name", "")
                tool_input = event["data"].get("input") or {}
                result = str(event["data"].get("output") or "")
                run_manager.broadcast(
                    run_id,
                    "planner_kb_tool_call",
                    {
                        "run_id": run_id,
                        "tool_name": tool_name,
                        "tool_args": tool_input,
                        "result": result,
                    },
                )

            # ------------------------------------------------------------------
            # LLM response complete
            # ------------------------------------------------------------------
            elif kind == "on_chat_model_end":
                output: AIMessage | None = event["data"].get("output")
                if output is None:
                    continue

                if "|" not in ns and node == "planner":
                    # Planner finished a turn.
                    reasoning = _extract_reasoning(output)
                    content_text = _extract_content(output)
                    raw_tcs = getattr(output, "tool_calls", None) or []
                    tool_calls = [
                        {
                            "agent": tc["name"],
                            "instructions": tc["args"].get("instructions", ""),
                            "execution_name": tc["args"].get("execution_name"),
                            # Raw args too — populated for every tool call kind (agent
                            # dispatch or kb_get/kb_list_dir), unlike the two fields
                            # above which are only meaningful for a dispatch call.
                            "args": tc["args"],
                        }
                        for tc in raw_tcs
                    ]
                    for tc in raw_tcs:
                        ctx.pending_instructions[tc["name"]] = tc["args"].get(
                            "instructions", ""
                        )
                        ctx.pending_execution_names[tc["name"]] = tc["args"].get(
                            "execution_name", ""
                        )
                    if not tool_calls:
                        final_report = content_text
                    usage = _extract_usage(output)
                    _account_usage(run_state, usage, token_budget)
                    run_manager.broadcast(
                        run_id,
                        "planner_message",
                        {
                            "run_id": run_id,
                            "reasoning": reasoning,
                            "content": content_text,
                            "tool_calls": tool_calls,
                            "usage": usage,
                        },
                    )

                elif node == "summarize" and "|" in ns:
                    # Summarizer LLM completed — pop the first pending tool result.
                    items = ctx.pending_summarize.get(ns, [])
                    if not items:
                        continue
                    ptc = items.pop(0)
                    if not items:
                        ctx.pending_summarize.pop(ns, None)
                    summary = _extract_content(output)
                    slug = _make_slug(ptc.tool_name, ptc.tool_args, label=ptc.kb_key)
                    base = f"{ptc.agent}/{slugify(ptc.execution_name or '')}/tool_logs/{slug}"
                    kb_key = f"{base}.md"
                    raw_kb_key = f"{base}_raw.json"
                    alerts_kb_key: str | None = (
                        f"{base}_alerts.json"
                        if ptc.raw_output and "alerts" in ptc.raw_output
                        else None
                    )
                    usage = _extract_usage(output)
                    _account_usage(run_state, usage, token_budget)
                    run_manager.broadcast(
                        run_id,
                        "subgraph_tool_call",
                        {
                            "run_id": run_id,
                            "agent": ptc.agent,
                            "execution_name": ptc.execution_name,
                            "tool_name": ptc.tool_name,
                            "tool_args": ptc.tool_args,
                            "raw_output": json.dumps(ptc.raw_output or {})[
                                :_RAW_OUTPUT_MAX
                            ],
                            "kb_key": kb_key,
                            "raw_kb_key": raw_kb_key,
                            "alerts_kb_key": alerts_kb_key,
                            "summary": summary,
                            "usage": usage,
                        },
                    )

                elif "|" in ns and node == "agent":
                    # Subgraph agent finished a turn.
                    reasoning = _extract_reasoning(output)
                    content_text = _extract_content(output)
                    raw_tcs = getattr(output, "tool_calls", None) or []
                    tool_calls = [
                        {"tool": tc["name"], "args": tc["args"]} for tc in raw_tcs
                    ]
                    usage = _extract_usage(output)
                    _account_usage(run_state, usage, token_budget)
                    run_manager.broadcast(
                        run_id,
                        "subgraph_agent_message",
                        {
                            "run_id": run_id,
                            "agent": agent,
                            "node": node,
                            "execution_name": ctx.pending_execution_names.get(agent),
                            "reasoning": reasoning,
                            "content": content_text,
                            "tool_calls": tool_calls,
                            "usage": usage,
                            "retry_count": ctx.pending_retry_counts.pop(ns, 0),
                        },
                    )

                elif "|" in ns and node == "reflect":
                    # Forced tool-less reflection checkpoint completed.
                    reasoning = _extract_reasoning(output)
                    content_text = _extract_content(output)
                    usage = _extract_usage(output)
                    _account_usage(run_state, usage, token_budget)
                    run_manager.broadcast(
                        run_id,
                        "subgraph_reflection",
                        {
                            "run_id": run_id,
                            "agent": agent,
                            "execution_name": ctx.pending_execution_names.get(agent),
                            "reasoning": reasoning,
                            "content": content_text,
                            "usage": usage,
                        },
                    )

            # ------------------------------------------------------------------
            # LLM call failed — only tracked for the agent node's transient
            # tool-call-parsing retries (see _invoke_agent_llm in subgraph.py).
            # Not re-broadcast as its own event; the count rides along on the
            # next successful subgraph_agent_message for the same ns.
            # ------------------------------------------------------------------
            elif kind == "on_chat_model_error" and "|" in ns and node == "agent":
                ctx.pending_retry_counts[ns] = ctx.pending_retry_counts.get(ns, 0) + 1

            # ------------------------------------------------------------------
            # Graph node started
            # ------------------------------------------------------------------
            elif kind == "on_chain_start" and node and _is_top_level_node(event, node):
                if "|" not in ns and node in ctx.agent_names:
                    # Subgraph node begins execution in the main graph.
                    # Reset the init-message guard so this fresh invocation emits
                    # system/human messages even if the same agent ran earlier.
                    ctx.emitted_init_messages.discard(node)
                    instructions = ctx.pending_instructions.get(node, "")
                    execution_name = ctx.pending_execution_names.get(node)
                    run_manager.broadcast(
                        run_id,
                        "subgraph_start",
                        {
                            "run_id": run_id,
                            "agent": node,
                            "execution_name": execution_name,
                            "instructions": instructions,
                        },
                    )
                elif (
                    "|" not in ns
                    and node == "planner"
                    and "planner" not in ctx.emitted_init_messages
                ):
                    # First planner invocation — emit initial system/human prompts.
                    ctx.emitted_init_messages.add("planner")
                    input_msgs = (event.get("data", {}).get("input") or {}).get(
                        "messages", []
                    )
                    for msg in input_msgs:
                        if isinstance(msg, SystemMessage):
                            role = "system"
                        elif isinstance(msg, HumanMessage):
                            role = "human"
                        else:
                            continue
                        content = msg.content if isinstance(msg.content, str) else ""
                        run_manager.broadcast(
                            run_id,
                            "subgraph_message",
                            {
                                "run_id": run_id,
                                "agent": "planner",
                                "role": role,
                                "content": content,
                            },
                        )
                elif (
                    node == "agent"
                    and "|" in ns
                    and _extract_agent(ns) not in ctx.emitted_init_messages
                ):
                    # First invocation of the agent node inside a compiled subgraph.
                    # Emit the initial system/human prompt messages so the frontend
                    # can display them — they are never otherwise sent as events.
                    # Keyed by agent name (not full ns) so re-invocations after tool
                    # calls (which get a fresh checkpoint UUID) don't re-emit.
                    agent_name = _extract_agent(ns)
                    ctx.emitted_init_messages.add(agent_name)
                    input_msgs = (event.get("data", {}).get("input") or {}).get(
                        "messages", []
                    )
                    for msg in input_msgs:
                        if isinstance(msg, SystemMessage):
                            role = "system"
                        elif isinstance(msg, HumanMessage):
                            role = "human"
                        else:
                            continue
                        content = msg.content if isinstance(msg.content, str) else ""
                        run_manager.broadcast(
                            run_id,
                            "subgraph_message",
                            {
                                "run_id": run_id,
                                "agent": agent_name,
                                "role": role,
                                "content": content,
                            },
                        )
                elif "|" in ns and node == "summarize":
                    # Read pending_tool_results from the node's input state so we
                    # can correlate each summarizer LLM call to the right tool result.
                    # (Tools are called synchronously inside zap_execute_node without
                    # propagating config, so on_tool_start/end events are unreliable.)
                    # Items with summarize=False skip the LLM call; emit their
                    # subgraph_tool_call event immediately from the raw output.
                    input_data = event.get("data", {}).get("input") or {}
                    raw_pending = input_data.get("pending_tool_results") or []
                    _execution_name = ctx.pending_execution_names.get(agent)
                    for item in raw_pending:
                        if item.get("summarize", True):
                            ctx.pending_summarize.setdefault(ns, []).append(
                                _PendingToolCall(
                                    agent=agent,
                                    tool_name=item.get("tool_name", ""),
                                    tool_args=item.get("tool_args", {}),
                                    raw_output=item.get("raw_output") or {},
                                    kb_key=item.get("kb_key"),
                                    execution_name=_execution_name,
                                )
                            )
                        else:
                            _tool_name = item.get("tool_name", "")
                            _tool_args = item.get("tool_args", {})
                            _raw = item.get("raw_output") or {}
                            _kb_key = item.get("kb_key")
                            slug = _make_slug(_tool_name, _tool_args, label=_kb_key)
                            base = f"{agent}/{slugify(_execution_name or '')}/tool_logs/{slug}"
                            raw_kb_key = f"{base}_raw.json"
                            alerts_kb_key: str | None = (
                                f"{base}_alerts.json" if "alerts" in _raw else None
                            )
                            run_manager.broadcast(
                                run_id,
                                "subgraph_tool_call",
                                {
                                    "run_id": run_id,
                                    "agent": agent,
                                    "execution_name": _execution_name,
                                    "tool_name": _tool_name,
                                    "tool_args": _tool_args,
                                    "raw_output": json.dumps(_raw)[
                                        :_RAW_OUTPUT_MAX
                                    ],
                                    "kb_key": raw_kb_key,
                                    "raw_kb_key": raw_kb_key,
                                    "alerts_kb_key": alerts_kb_key,
                                    "summary": None,
                                },
                            )
                run_manager.broadcast(
                    run_id,
                    "node_start",
                    {
                        "run_id": run_id,
                        "agent": agent,
                        "node": node,
                    },
                )

            # ------------------------------------------------------------------
            # Graph node finished
            # ------------------------------------------------------------------
            elif kind == "on_chain_end" and node and _is_top_level_node(event, node):
                if "|" not in ns and node in ctx.agent_names:
                    # Subgraph node returned its result to the main graph.
                    msgs = (event["data"].get("output") or {}).get("messages", [])
                    result = msgs[-1].content if msgs else ""
                    run_manager.broadcast(
                        run_id,
                        "subgraph_end",
                        {
                            "run_id": run_id,
                            "agent": node,
                            "execution_name": ctx.pending_execution_names.get(node),
                            "result": result,
                        },
                    )
                elif "|" in ns and node in {"summarize", "kb_tools"}:
                    # Poll KB for changes.
                    # summarize_node stores ZAP tool results; kb_tools (ToolNode)
                    # handles register_finding which also writes to KB.
                    if run_state.kb is not None:
                        current_keys = run_state.kb.list_keys()
                        if current_keys != ctx.prev_kb_keys:
                            ctx.prev_kb_keys = current_keys
                            run_manager.broadcast(
                                run_id,
                                "kb_update",
                                {
                                    "run_id": run_id,
                                    "keys": current_keys,
                                },
                            )
                run_manager.broadcast(
                    run_id,
                    "node_end",
                    {
                        "run_id": run_id,
                        "agent": agent,
                        "node": node,
                    },
                )

        run_state.status = RunStatus.COMPLETED
        run_state.ended_at = datetime.now(timezone.utc)
        logger.info("Run %s completed.", run_id)

    except asyncio.CancelledError:
        run_state.status = RunStatus.CANCELLED
        run_state.ended_at = datetime.now(timezone.utc)
        logger.info("Run %s cancelled.", run_id)
        raise

    except Exception as exc:
        run_state.status = RunStatus.FAILED
        run_state.ended_at = datetime.now(timezone.utc)
        run_state.error = str(exc)
        logger.exception("Run %s failed: %s", run_id, exc)
        run_manager.broadcast(
            run_id,
            "error",
            {
                "run_id": run_id,
                "message": str(exc),
            },
        )

    finally:
        # Explicitly close the event stream generator. For normal completion the
        # generator is already exhausted (no-op). For failed runs (GraphRecursionError,
        # app crashes, etc.) the generator is still open; aclose() injects GeneratorExit
        # into LangGraph's body so its cleanup callbacks run before we move on.
        try:
            await _event_stream.aclose()
        except BaseException as exc:
            logger.warning("Event stream close interrupted for run %s: %s", run_id, exc)
        # Parse the planner's "Findings Summary" table (see report_parser.py)
        # into a structured list for later comparison against ground truth.
        run_state.findings = parse_findings_table(final_report)
        _final_status_payload = {
            "run_id": run_id,
            "status": run_state.status,
            "error": run_state.error,
        }
        run_manager.broadcast(run_id, "run_status", _final_status_payload)
        run_manager.broadcast_global("run_status", _final_status_payload)
        try:
            run_manager.persist_run(run_id, runs_dir)
        except Exception as exc:
            logger.error("Failed to persist run %s: %s", run_id, exc)
        run_manager.close_broadcast(run_id)


def build_initial_state(planner_cfg: dict, target: str) -> dict[str, Any]:
    """Build the initial graph state dict from planner config and target URL."""
    return {
        "target": target,
        "messages": ChatPromptTemplate(
            dict_to_tuple_list(planner_cfg["prompts"])
        ).format_messages(target=target),
    }


# Module-level singleton — imported by api.py.
run_manager = RunManager()
