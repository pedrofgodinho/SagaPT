"""Unit tests for export_stats — CSV export of a run's persisted trace.json."""

import json

from export_stats import build_findings, build_invocations, build_llm_calls, build_run_summary


def _event(etype: str, ts: str, **payload) -> dict:
    return {"type": etype, "payload": {"run_id": "r1", **payload}, "ts": ts}


def _usage(input_tokens=100, output_tokens=50, cached_input_tokens=0, model_name="test-model"):
    return {
        "model_name": model_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cached_input_tokens": cached_input_tokens,
        "reasoning_tokens": 0,
    }


def _trace(events: list[dict], **overrides) -> dict:
    trace = {
        "run_id": "r1",
        "name": "Run #1",
        "target": "http://example.com",
        "status": "completed",
        "started_at": "2026-01-01T00:00:00+00:00",
        "ended_at": "2026-01-01T00:10:00+00:00",
        "agent_config": {
            "recon_agent": {"max_tool_calls": 3, "reflection_interval": 8, "model_name": "test-model"},
            "dast_agent": {"max_tool_calls": 28, "reflection_interval": 8, "model_name": "test-model"},
        },
        "findings": [
            {"endpoint": "/login", "vulnerability": "SQL Injection", "poc": "' OR 1=1 --"},
        ],
        "events": events,
    }
    trace.update(overrides)
    return trace


def _synthetic_events() -> list[dict]:
    """One recon invocation that hits its hard cap, then one dast invocation
    exercising retries, an empty-response nudge, a multi-turn tool sequence
    around a reflection, and a genuine final wrap-up turn, then a second
    dast invocation with no usage data at all (simulates a pre-
    instrumentation trace).

    recon_agent: max_tool_calls=3 in agent_config; 3 tool calls issued -> hard cap hit.
    dast "sqli-probe": retry -> empty nudge -> calls http_get -> reflects ->
    calls register_finding -> final wrap-up message.
    dast "xss-probe": one tool call, no usage anywhere in the invocation.
    """
    return [
        _event("planner_message", "2026-01-01T00:00:00+00:00", reasoning=None, content="",
               tool_calls=[{"agent": "recon_agent", "instructions": "map it", "execution_name": "initial_recon", "args": {}}],
               usage=_usage(200, 20)),
        _event("subgraph_start", "2026-01-01T00:00:01+00:00", agent="recon_agent", execution_name="initial_recon", instructions="map it"),
        _event("subgraph_agent_message", "2026-01-01T00:00:02+00:00", agent="recon_agent", node="agent",
               execution_name="initial_recon", reasoning=None, content="calling tool",
               tool_calls=[{"tool": "http_get", "args": {}}], usage=_usage(10, 5), retry_count=0),
        _event("subgraph_tool_call", "2026-01-01T00:00:03+00:00", agent="recon_agent", execution_name="initial_recon",
               tool_name="http_get", tool_args={}, raw_output="{}", kb_key="k1", raw_kb_key="k1r", alerts_kb_key=None,
               summary="ok", usage=_usage(30, 8)),
        _event("subgraph_agent_message", "2026-01-01T00:00:04+00:00", agent="recon_agent", node="agent",
               execution_name="initial_recon", reasoning=None, content="calling tool",
               tool_calls=[{"tool": "http_get", "args": {}}], usage=_usage(10, 5), retry_count=0),
        _event("subgraph_tool_call", "2026-01-01T00:00:05+00:00", agent="recon_agent", execution_name="initial_recon",
               tool_name="http_get", tool_args={}, raw_output="{}", kb_key="k2", raw_kb_key="k2r", alerts_kb_key=None,
               summary="ok", usage=_usage(30, 8)),
        _event("subgraph_agent_message", "2026-01-01T00:00:06+00:00", agent="recon_agent", node="agent",
               execution_name="initial_recon", reasoning=None, content="calling tool",
               tool_calls=[{"tool": "http_get", "args": {}}], usage=_usage(10, 5), retry_count=0),
        _event("subgraph_tool_call", "2026-01-01T00:00:07+00:00", agent="recon_agent", execution_name="initial_recon",
               tool_name="http_get", tool_args={}, raw_output="{}", kb_key="k3", raw_kb_key="k3r", alerts_kb_key=None,
               summary="ok", usage=_usage(30, 8)),
        _event("subgraph_end", "2026-01-01T00:00:08+00:00", agent="recon_agent", execution_name="initial_recon", result="done"),

        _event("planner_message", "2026-01-01T00:00:09+00:00", reasoning=None, content="",
               tool_calls=[{"agent": "dast_agent", "instructions": "probe sqli", "execution_name": "sqli-probe", "args": {}}],
               usage=_usage(200, 20)),
        _event("subgraph_start", "2026-01-01T00:00:10+00:00", agent="dast_agent", execution_name="sqli-probe", instructions="probe sqli"),
        # A retryable parse failure occurred before this successful call (retry_count=1).
        _event("subgraph_agent_message", "2026-01-01T00:00:11+00:00", agent="dast_agent", node="agent",
               execution_name="sqli-probe", reasoning=None, content="", tool_calls=[], usage=None, retry_count=1),
        # Empty-response nudge (no retry_count — this is the *other* retry path).
        _event("subgraph_agent_message", "2026-01-01T00:00:12+00:00", agent="dast_agent", node="agent",
               execution_name="sqli-probe", reasoning=None, content="", tool_calls=[], usage=_usage(15, 2), retry_count=0),
        # First real decision: calls http_get.
        _event("subgraph_agent_message", "2026-01-01T00:00:13+00:00", agent="dast_agent", node="agent",
               execution_name="sqli-probe", reasoning=None, content="checking sqli",
               tool_calls=[{"tool": "http_get", "args": {}}], usage=_usage(15, 2), retry_count=0),
        _event("subgraph_tool_call", "2026-01-01T00:00:14+00:00", agent="dast_agent", execution_name="sqli-probe",
               tool_name="http_get", tool_args={}, raw_output="{}", kb_key="k5", raw_kb_key="k5r", alerts_kb_key=None,
               summary="ok", usage=_usage(20, 5)),
        _event("subgraph_reflection", "2026-01-01T00:00:15+00:00", agent="dast_agent", execution_name="sqli-probe",
               reasoning=None, content="looks confirmed", usage=_usage(50, 10)),
        # Second real decision, after the reflection: registers the finding.
        _event("subgraph_agent_message", "2026-01-01T00:00:16+00:00", agent="dast_agent", node="agent",
               execution_name="sqli-probe", reasoning=None, content="",
               tool_calls=[{"tool": "register_finding", "args": {}}], usage=_usage(12, 3), retry_count=0),
        _event("subgraph_kb_tool_call", "2026-01-01T00:00:17+00:00", agent="dast_agent",
               tool_name="register_finding", tool_args={"title": "SQLi"}, result="ok"),
        # Final wrap-up turn: has content, calls no further tools.
        _event("subgraph_agent_message", "2026-01-01T00:00:18+00:00", agent="dast_agent", node="agent",
               execution_name="sqli-probe", reasoning=None, content="found it, sqli confirmed",
               tool_calls=[], usage=_usage(15, 2), retry_count=0),
        _event("subgraph_end", "2026-01-01T00:00:19+00:00", agent="dast_agent", execution_name="sqli-probe", result="done"),

        _event("planner_message", "2026-01-01T00:00:20+00:00", reasoning=None, content="",
               tool_calls=[{"agent": "dast_agent", "instructions": "probe xss", "execution_name": "xss-probe", "args": {}}],
               usage=_usage(200, 20)),
        _event("subgraph_start", "2026-01-01T00:00:21+00:00", agent="dast_agent", execution_name="xss-probe", instructions="probe xss"),
        # No usage anywhere in this invocation -- simulates a pre-instrumentation trace.
        _event("subgraph_agent_message", "2026-01-01T00:00:22+00:00", agent="dast_agent", node="agent",
               execution_name="xss-probe", reasoning=None, content="testing xss",
               tool_calls=[{"tool": "http_get", "args": {}}], usage=None, retry_count=0),
        _event("subgraph_tool_call", "2026-01-01T00:00:23+00:00", agent="dast_agent", execution_name="xss-probe",
               tool_name="http_get", tool_args={}, raw_output="{}", kb_key="k6", raw_kb_key="k6r", alerts_kb_key=None,
               summary=None),
        _event("subgraph_end", "2026-01-01T00:00:24+00:00", agent="dast_agent", execution_name="xss-probe", result="done"),
    ]


def test_build_invocations_pairing_and_order():
    trace = _trace(_synthetic_events())
    invocations = build_invocations(trace)

    assert [inv["agent"] for inv in invocations] == ["recon_agent", "dast_agent", "dast_agent"]
    assert [inv["execution_name"] for inv in invocations] == ["initial_recon", "sqli-probe", "xss-probe"]
    assert [inv["order_index"] for inv in invocations] == [0, 1, 2]


def test_build_invocations_hard_cap_detection():
    trace = _trace(_synthetic_events())
    invocations = build_invocations(trace)

    recon = invocations[0]
    assert recon["num_tool_calls"] == 3
    assert recon["hit_hard_cap"] is True  # max_tool_calls=3 in agent_config

    sqli = invocations[1]
    assert sqli["num_tool_calls"] == 1  # one http_get
    assert sqli["hit_hard_cap"] is False  # max_tool_calls=28


def test_build_invocations_retry_and_reflection_and_findings():
    trace = _trace(_synthetic_events())
    invocations = build_invocations(trace)
    sqli = invocations[1]

    assert sqli["retry_count"] == 1
    assert sqli["num_empty_retries"] == 2  # both empty-content/no-tool-call turns count
    assert sqli["num_reflections"] == 1
    assert sqli["num_findings_registered"] == 1


def test_build_invocations_token_sums():
    trace = _trace(_synthetic_events())
    invocations = build_invocations(trace)
    recon = invocations[0]

    # 3x agent_message(10,5) + 3x tool_call(30,8) = (30+90, 15+24) = (120, 39)
    assert recon["input_tokens"] == 120
    assert recon["output_tokens"] == 39
    assert recon["total_tokens"] == 159

    xss = invocations[2]
    assert xss["input_tokens"] == 0  # no event in this invocation has usage at all


def test_build_invocations_missing_usage_degrades_gracefully():
    """An event with usage=None (old pre-instrumentation trace) must not crash."""
    trace = _trace(_synthetic_events())
    invocations = build_invocations(trace)
    sqli = invocations[1]
    # ts11 (retry) had usage=None and contributes nothing; the rest
    # (ts12, ts13, ts14, ts15, ts16, ts18) sum normally.
    assert sqli["input_tokens"] == 15 + 15 + 20 + 50 + 12 + 15
    assert sqli["output_tokens"] == 2 + 2 + 5 + 10 + 3 + 2


def test_build_llm_calls_call_types_and_summarizer_detection():
    trace = _trace(_synthetic_events())
    calls = build_llm_calls(trace)
    call_types = [c["call_type"] for c in calls]

    assert call_types.count("planner") == 3
    assert call_types.count("agent") == 9  # 3 recon + 5 sqli + 1 xss agent messages
    assert call_types.count("reflect") == 1
    # recon's 3 tool_calls + sqli's http_get all carry a "usage" key; xss's
    # tool_call has none, so it must NOT show up as its own call.
    assert call_types.count("summarizer") == 4


def test_build_llm_calls_tool_calls_and_durations_single_tool():
    trace = _trace(_synthetic_events())
    calls = build_llm_calls(trace)
    recon_agent_calls = [c for c in calls if c["call_type"] == "agent" and c["agent"] == "recon_agent"]

    assert len(recon_agent_calls) == 3
    for call in recon_agent_calls:
        assert json.loads(call["tool_calls"]) == ["http_get"]
        assert json.loads(call["tool_durations"]) == [1.0]
        assert call["has_content"] is True


def test_build_llm_calls_empty_nudge_vs_final_report():
    trace = _trace(_synthetic_events())
    calls = build_llm_calls(trace)
    sqli_agent_calls = [
        c for c in calls if c["call_type"] == "agent" and c["execution_name"] == "sqli-probe"
    ]
    assert len(sqli_agent_calls) == 5

    retry, nudge, http_call, kb_call, final = sqli_agent_calls

    # The retryable turn and the empty-response nudge both called no tool
    # and have no content -- indistinguishable from each other, but both
    # distinguishable from the final report via has_content.
    assert retry["has_content"] is False and json.loads(retry["tool_calls"]) == []
    assert retry["retry_count"] == 1
    assert nudge["has_content"] is False and json.loads(nudge["tool_calls"]) == []

    assert json.loads(http_call["tool_calls"]) == ["http_get"]
    assert json.loads(kb_call["tool_calls"]) == ["register_finding"]

    # The final wrap-up turn: has content, called no further tools -- this
    # is what used to need a dedicated "final_report" marker in an earlier
    # design; here it's just an ordinary agent row with an empty tool list.
    assert final["has_content"] is True
    assert json.loads(final["tool_calls"]) == []


def test_build_llm_calls_tool_duration_gap_since_previous_event():
    trace = _trace(_synthetic_events())
    calls = build_llm_calls(trace)
    http_call = next(
        c for c in calls
        if c["call_type"] == "agent" and c["execution_name"] == "sqli-probe" and json.loads(c["tool_calls"]) == ["http_get"]
    )
    # decision@13 -> tool_call@14: 1 second gap.
    assert json.loads(http_call["tool_durations"]) == [1.0]


def test_build_llm_calls_tool_call_survives_missing_usage():
    """xss-probe's tool_call has no usage key at all -- it must still show up
    in tool_calls/tool_durations (just contribute no tokens), not vanish."""
    trace = _trace(_synthetic_events())
    calls = build_llm_calls(trace)
    xss_call = next(c for c in calls if c["call_type"] == "agent" and c["execution_name"] == "xss-probe")

    assert json.loads(xss_call["tool_calls"]) == ["http_get"]
    assert json.loads(xss_call["tool_durations"]) == [1.0]
    assert xss_call["input_tokens"] == 0  # the decision itself had usage=None
    # No separate "summarizer" row for a tool_call with no usage key.
    assert not any(
        c["call_type"] == "summarizer" and c["execution_name"] == "xss-probe" for c in calls
    )


def test_build_run_summary_invocation_sequence_and_totals():
    trace = _trace(_synthetic_events())
    summary = build_run_summary(trace)

    assert summary["invocation_sequence"] == "recon_agent,dast_agent,dast_agent"
    assert summary["num_agent_invocations"] == 3
    assert summary["num_hit_hard_cap"] == 1
    assert summary["total_kb_findings_registered"] == 1
    assert summary["total_reflections"] == 1
    assert summary["total_retries"] == 1
    assert summary["num_findings"] == 1
    assert summary["duration_s"] == 600.0


def test_build_findings():
    trace = _trace(_synthetic_events())
    findings = build_findings(trace)
    assert findings == [
        {"run_id": "r1", "endpoint": "/login", "vulnerability": "SQL Injection", "poc": "' OR 1=1 --"},
    ]


def test_build_invocations_unmatched_trailing_start():
    """A run cancelled mid-invocation leaves a subgraph_start with no matching end."""
    events = [
        _event("subgraph_start", "2026-01-01T00:00:00+00:00", agent="recon_agent", execution_name="initial_recon", instructions=""),
        _event("subgraph_agent_message", "2026-01-01T00:00:01+00:00", agent="recon_agent", node="agent",
               execution_name="initial_recon", reasoning=None, content="working", tool_calls=[], usage=_usage(5, 5), retry_count=0),
    ]
    trace = _trace(events, status="cancelled")
    invocations = build_invocations(trace)

    assert len(invocations) == 1
    assert invocations[0]["end_ts"] is None
    assert invocations[0]["duration_s"] is None
    assert invocations[0]["hit_hard_cap"] is False
