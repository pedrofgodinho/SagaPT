"""Export a run's persisted trace.json into CSVs for offline statistical analysis.

Pure functions operate on an already-loaded trace dict (see ``load_trace``),
mirroring ``report_parser.py``'s style: no I/O in the core logic, easy to
unit test against a hand-built fixture. ``export_run``/``export_all`` are the
only functions that touch the filesystem.

Agent dispatch is strictly sequential (the planner may only dispatch one
agent per turn — see ``main_graph.py``), so ``subgraph_start``/``subgraph_end``
events never interleave across agents. This lets every ``build_*`` function
here do a single forward pass over ``trace["events"]``, tracking at most one
"open" agent invocation at a time.
"""

import csv
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

# Event types that occur *inside* an agent invocation window and are
# attributed to the currently open invocation.
_IN_INVOCATION_EVENT_TYPES = frozenset(
    {"subgraph_agent_message", "subgraph_tool_call", "subgraph_reflection", "subgraph_kb_tool_call"}
)

_ZERO_USAGE = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cached_input_tokens": 0,
    "reasoning_tokens": 0,
    "total_tokens": 0,
}


def load_trace(run_dir: Path) -> dict[str, Any]:
    """Load ``{run_dir}/trace.json``."""
    return json.loads((run_dir / "trace.json").read_text(encoding="utf-8"))


def _parse_ts(ts: str) -> datetime:
    """Parse a StoredEvent's ISO-8601 ``ts`` field."""
    return datetime.fromisoformat(ts)


def _usage_or_zero(usage: dict | None) -> dict:
    """Return an event payload's ``usage`` field, or a zeroed dict if absent."""
    return usage if usage else dict(_ZERO_USAGE)


class _OpenInvocation:
    """Accumulator for one agent invocation, from subgraph_start to subgraph_end."""

    def __init__(self, order_index: int, start_event: dict) -> None:
        payload = start_event["payload"]
        self.order_index = order_index
        self.agent: str = payload["agent"]
        self.execution_name: str | None = payload.get("execution_name")
        self.start_ts: str = start_event["ts"]
        self.end_ts: str | None = None
        self.num_tool_calls = 0
        self.num_kb_tool_calls = 0
        self.num_reflections = 0
        self.num_findings_registered = 0
        self.num_empty_retries = 0
        self.retry_count = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_input_tokens = 0
        self.reasoning_tokens = 0
        self.total_tokens = 0

    def add_usage(self, usage: dict | None) -> None:
        if usage:
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)
            self.cached_input_tokens += usage.get("cached_input_tokens", 0)
            self.reasoning_tokens += usage.get("reasoning_tokens", 0)
            self.total_tokens += usage.get("total_tokens", 0)

    def apply_event(self, event: dict) -> None:
        etype = event["type"]
        payload = event["payload"]
        if payload.get("agent") != self.agent:
            return
        if etype == "subgraph_tool_call":
            self.num_tool_calls += 1
            if "usage" in payload:
                self.add_usage(payload.get("usage"))
        elif etype == "subgraph_agent_message":
            self.add_usage(payload.get("usage"))
            self.retry_count += payload.get("retry_count", 0) or 0
            if not payload.get("content") and not payload.get("tool_calls"):
                self.num_empty_retries += 1
        elif etype == "subgraph_reflection":
            self.num_reflections += 1
            self.add_usage(payload.get("usage"))
        elif etype == "subgraph_kb_tool_call":
            self.num_kb_tool_calls += 1
            if payload.get("tool_name") == "register_finding":
                self.num_findings_registered += 1

    def finalize(self, end_event: dict | None, agent_config: dict) -> dict:
        if end_event is not None:
            self.end_ts = end_event["ts"]
            duration_s = (
                _parse_ts(self.end_ts) - _parse_ts(self.start_ts)
            ).total_seconds()
        else:
            duration_s = None
        max_tool_calls = agent_config.get(self.agent, {}).get("max_tool_calls", math.inf)
        return {
            "order_index": self.order_index,
            "agent": self.agent,
            "execution_name": self.execution_name,
            "start_ts": self.start_ts,
            "end_ts": self.end_ts,
            "duration_s": duration_s,
            "num_tool_calls": self.num_tool_calls,
            "num_kb_tool_calls": self.num_kb_tool_calls,
            "num_reflections": self.num_reflections,
            "num_findings_registered": self.num_findings_registered,
            "retry_count": self.retry_count,
            "num_empty_retries": self.num_empty_retries,
            "hit_hard_cap": self.num_tool_calls >= max_tool_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "total_tokens": self.total_tokens,
        }


def build_invocations(trace: dict[str, Any]) -> list[dict]:
    """One row per agent invocation (subgraph_start → subgraph_end pair), in order."""
    agent_config = trace.get("agent_config", {})
    rows: list[dict] = []
    current: _OpenInvocation | None = None
    order_index = 0

    for event in trace.get("events", []):
        etype = event["type"]
        if etype == "subgraph_start":
            if current is not None:
                # Shouldn't happen (dispatch is strictly sequential) — close the
                # stale invocation as unmatched rather than silently dropping it.
                rows.append(current.finalize(None, agent_config))
            current = _OpenInvocation(order_index, event)
            order_index += 1
        elif etype == "subgraph_end" and current is not None:
            rows.append(current.finalize(event, agent_config))
            current = None
        elif current is not None and etype in _IN_INVOCATION_EVENT_TYPES:
            current.apply_event(event)

    if current is not None:
        # Run ended (cancelled/failed) mid-invocation.
        rows.append(current.finalize(None, agent_config))

    return rows


def build_llm_calls(trace: dict[str, Any]) -> list[dict]:
    """One row per individual LLM call (planner/agent/summarizer/reflect turns).

    "agent" rows additionally carry ``tool_calls``/``tool_durations`` (JSON-
    encoded lists, since a CSV cell can't hold a native list) — the ZAP/KB
    tool(s) that turn's decision resulted in, and how long each one took. A
    single agent turn can call more than one tool (the ReAct loop allows
    mixed ZAP+KB turns), which is exactly why these are lists rather than
    one tool per row: a tool call doesn't stand on its own, it's always the
    result of one specific LLM decision, and modeling it as a peer-level
    "step" (an earlier version of this function's design) obscured that
    parent/child relationship.

    A tool's duration is the gap since the previous event in the same turn
    (the turn's own ``ts`` for the first tool, then each tool's own ``ts``
    after that) — no individual ZAP/KB tool execution carries its own
    duration anywhere in ``trace.json``, so this is the closest available
    proxy, and it has the side effect of attributing the turn's own
    thinking/generation time to the first tool it called. Both lists are
    ``[]`` for non-"agent" rows, and for "agent" rows that called no tool —
    which happens for two different reasons ``has_content`` tells apart: an
    empty-response nudge (no content either) vs. the genuine final wrap-up
    turn that ends the invocation (has content, calls no further tools).
    """
    rows: list[dict] = []
    order_index = 0
    # Reference to the still-being-filled "agent" row already appended to
    # `rows` — later tool-call events mutate it in place (rather than
    # deferring its append), which keeps `rows` in strict chronological
    # order even though a turn's tool calls are only known *after* the
    # decision that produced them.
    pending: dict | None = None
    pending_prev_ts: str | None = None

    for event in trace.get("events", []):
        etype = event["type"]
        payload = event["payload"]

        if etype in ("subgraph_start", "subgraph_end"):
            # Dispatch is strictly sequential (see module docstring), so a
            # stray tool-call event can never legitimately arrive between
            # invocations -- clearing here is a defensive belt-and-braces
            # measure, not something the real graph should ever need.
            pending = None
            continue

        if etype in ("subgraph_tool_call", "subgraph_kb_tool_call") and pending is not None:
            ts = event["ts"]
            pending["tool_calls"].append(payload.get("tool_name", ""))
            pending["tool_durations"].append(
                (_parse_ts(ts) - _parse_ts(pending_prev_ts)).total_seconds()
            )
            pending_prev_ts = ts
            if etype == "subgraph_tool_call" and "usage" in payload:
                # Also its own LLM call (the summarizer) -- doesn't
                # interrupt the pending agent row, which keeps accumulating.
                usage = _usage_or_zero(payload.get("usage"))
                rows.append(
                    {
                        "order_index": order_index,
                        "call_type": "summarizer",
                        "agent": payload.get("agent"),
                        "execution_name": payload.get("execution_name"),
                        "model_name": (payload.get("usage") or {}).get("model_name"),
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "cached_input_tokens": usage.get("cached_input_tokens", 0),
                        "reasoning_tokens": usage.get("reasoning_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                        "retry_count": 0,
                        "has_content": True,
                        "tool_calls": [],
                        "tool_durations": [],
                        "ts": ts,
                    }
                )
                order_index += 1
            continue

        call_type: str | None = None
        agent: str | None = None
        execution_name: str | None = None

        if etype == "planner_message":
            call_type = "planner"
        elif etype == "subgraph_agent_message":
            call_type = "agent"
            agent = payload.get("agent")
            execution_name = payload.get("execution_name")
        elif etype == "subgraph_reflection":
            call_type = "reflect"
            agent = payload.get("agent")
            execution_name = payload.get("execution_name")
        elif etype == "subgraph_tool_call" and "usage" in payload:
            # A summarizer call with no open agent turn to attach to
            # (pending is None) -- shouldn't happen given the invariant
            # above, handled for completeness rather than silently dropped.
            call_type = "summarizer"
            agent = payload.get("agent")
            execution_name = payload.get("execution_name")
        else:
            continue

        if call_type in ("agent", "reflect"):
            # Whatever agent turn was pending is done -- either superseded
            # by a fresh decision, or closed out by a reflection checkpoint.
            pending = None

        usage = _usage_or_zero(payload.get("usage"))
        row = {
            "order_index": order_index,
            "call_type": call_type,
            "agent": agent,
            "execution_name": execution_name,
            "model_name": (payload.get("usage") or {}).get("model_name"),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cached_input_tokens": usage.get("cached_input_tokens", 0),
            "reasoning_tokens": usage.get("reasoning_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "retry_count": payload.get("retry_count", 0) if call_type == "agent" else 0,
            "has_content": bool(payload.get("content")),
            "tool_calls": [],
            "tool_durations": [],
            "ts": event["ts"],
        }
        rows.append(row)
        order_index += 1

        if call_type == "agent":
            pending = row
            pending_prev_ts = event["ts"]

    for row in rows:
        row["tool_calls"] = json.dumps(row["tool_calls"])
        row["tool_durations"] = json.dumps(row["tool_durations"])

    return rows


def build_findings(trace: dict[str, Any]) -> list[dict]:
    """Raw endpoint/vulnerability/PoC rows from the planner's final report."""
    run_id = trace["run_id"]
    return [
        {
            "run_id": run_id,
            "endpoint": f["endpoint"],
            "vulnerability": f["vulnerability"],
            "poc": f["poc"],
        }
        for f in trace.get("findings", [])
    ]


def build_run_summary(trace: dict[str, Any]) -> dict:
    """One row summarizing the whole run."""
    invocations = build_invocations(trace)
    llm_calls = build_llm_calls(trace)

    started_at = trace.get("started_at")
    ended_at = trace.get("ended_at")
    duration_s = (
        (_parse_ts(ended_at) - _parse_ts(started_at)).total_seconds()
        if started_at and ended_at
        else None
    )

    return {
        "run_id": trace["run_id"],
        "name": trace.get("name"),
        "target": trace.get("target"),
        "status": trace.get("status"),
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_s": duration_s,
        "num_agent_invocations": len(invocations),
        "invocation_sequence": ",".join(inv["agent"] for inv in invocations),
        "total_llm_calls": len(llm_calls),
        "total_tool_calls": sum(inv["num_tool_calls"] for inv in invocations),
        "total_kb_findings_registered": sum(
            inv["num_findings_registered"] for inv in invocations
        ),
        "total_reflections": sum(inv["num_reflections"] for inv in invocations),
        "total_retries": sum(inv["retry_count"] for inv in invocations),
        "num_hit_hard_cap": sum(1 for inv in invocations if inv["hit_hard_cap"]),
        "total_input_tokens": sum(c["input_tokens"] for c in llm_calls),
        "total_output_tokens": sum(c["output_tokens"] for c in llm_calls),
        "total_cached_input_tokens": sum(c["cached_input_tokens"] for c in llm_calls),
        "total_reasoning_tokens": sum(c["reasoning_tokens"] for c in llm_calls),
        "total_tokens": sum(c["total_tokens"] for c in llm_calls),
        "num_findings": len(trace.get("findings", [])),
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    """Write ``rows`` as CSV, or an empty file with no rows if the list is empty."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def export_run(run_dir: Path, out_dir: Path | None = None) -> Path:
    """Export one run's trace.json to CSVs. Returns the output directory used."""
    trace = load_trace(run_dir)
    out_dir = out_dir or (run_dir / "export")
    _write_csv(out_dir / "invocations.csv", build_invocations(trace))
    _write_csv(out_dir / "llm_calls.csv", build_llm_calls(trace))
    _write_csv(out_dir / "findings.csv", build_findings(trace))
    _write_csv(out_dir / "run_summary.csv", [build_run_summary(trace)])
    return out_dir


def export_all(runs_dir: Path, out_dir: Path) -> Path:
    """Export every persisted run under ``runs_dir``.

    Writes per-run CSVs into each run's own ``export/`` directory, and
    combined cross-run CSVs (``all_*.csv``) into ``out_dir`` for aggregate
    analysis across the full thesis dataset.
    """
    all_summaries: list[dict] = []
    all_invocations: list[dict] = []
    all_llm_calls: list[dict] = []
    all_findings: list[dict] = []

    for trace_path in sorted(runs_dir.glob("*/trace.json")):
        run_dir = trace_path.parent
        trace = load_trace(run_dir)
        export_run(run_dir, run_dir / "export")

        all_summaries.append(build_run_summary(trace))
        run_id = trace["run_id"]
        for row in build_invocations(trace):
            all_invocations.append({"run_id": run_id, **row})
        for row in build_llm_calls(trace):
            all_llm_calls.append({"run_id": run_id, **row})
        all_findings.extend(build_findings(trace))

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(out_dir / "all_runs_summary.csv", all_summaries)
    _write_csv(out_dir / "all_invocations.csv", all_invocations)
    _write_csv(out_dir / "all_llm_calls.csv", all_llm_calls)
    _write_csv(out_dir / "all_findings.csv", all_findings)
    return out_dir
