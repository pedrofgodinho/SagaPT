"""End-to-end tests for SSE event emission in the SagaPT API.

These tests run entirely in-process — no ZAP, no Ollama, no external LLM
providers are required.  Fake models and a fake tool are injected before
each test and torn down afterward.

Test scenario
-------------
The planner calls the ``recon`` agent, which calls the ``fake_http_get`` tool.
The summariser compresses the tool output and stores it in the knowledge base.
The agent produces a final text message, which feeds back to the planner as a
``ToolMessage``.  The planner then emits a final text response and the graph
terminates.

Expected SSE events (at minimum):
    run_status, planner_message, subgraph_start, subgraph_agent_message,
    subgraph_tool_call, subgraph_end, kb_update, node_start, node_end
"""

import json

import pytest
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Fake run configuration — mirrors saga.toml structure exactly
# ---------------------------------------------------------------------------

FAKE_RUN_CONFIG: dict = {
    "general": {"target": "http://fake-target"},
    "summarizer": {
        "model_provider": "fake",
        "model_name": "fake-summarizer",
        "temperature": 0,
        "prompts": {
            "system": "Summarize the tool output concisely.",
            "human": "Tool: {tool_name}\nArgs: {tool_args}\nOutput:\n{raw_output}",
        },
    },
    "planner": {
        "model_provider": "fake",
        "model_name": "fake-planner",
        "temperature": 0,
        "prompts": {
            "system": "You are a security testing planner.",
            "human": "Target: {target}.",
        },
    },
    "agents": {
        "recon": {
            "name": "recon",
            "description": "Performs reconnaissance on the target.",
            "tools": [{"name": "fake_http_get", "summarize": True}],
            "model_provider": "fake",
            "model_name": "fake-agent",
            "temperature": 0,
            "reflection_interval": 2,
            "max_tool_calls": 5,
            "prompts": {
                "system": "You are a recon agent.",
                "human": "Target: {target}. Task: {task}\nKB: {kb_keys}",
            },
        }
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_models():
    """Register deterministic fake LLMs for planner, agent, and summariser.

    Teardown clears all fake models and both model caches so subsequent tests
    start with a clean slate.
    """
    from fakes.fake_llm import FakeChatModel
    from model_factory import clear_fake_models, register_fake_model

    # Planner:
    #   - First call (HumanMessage "Target: http://fake-target."): call recon agent.
    #   - Second call (ToolMessage "Reconnaissance complete."): emit final text.
    register_fake_model(
        "fake-planner",
        FakeChatModel(responses=[
            (
                "Reconnaissance complete",
                "Penetration test complete.\n\n"
                "## Findings Summary\n\n"
                "| Endpoint | Vulnerability | PoC |\n"
                "| --- | --- | --- |\n"
                "| /login | SQL Injection | admin' OR '1'='1 |\n",
            ),
            (
                "",
                [{
                    "name": "recon",
                    "args": {
                        "instructions": "Scan http://fake-target.",
                        "execution_name": "Initial recon",
                    },
                }],
            ),
        ]),
    )

    # Agent:
    #   - First call (HumanMessage with task text): call fake_http_get.
    #   - Second call (ToolMessage with GET result): emit final summary.
    register_fake_model(
        "fake-agent",
        FakeChatModel(responses=[
            ("200", "Reconnaissance complete."),
            (
                "",
                [{"name": "fake_http_get", "args": {"url": "http://fake-target"}}],
            ),
        ]),
    )

    # Summariser: always returns a JSON string that deserialises into
    # _SummariserOutput(key=..., summary=...).
    register_fake_model(
        "fake-summarizer",
        FakeChatModel(responses=[
            (
                "",
                '{"key": "fake_http_get http://fake-target - 200 OK", "summary": "GET returned 200 OK."}',
            ),
        ]),
    )

    yield

    clear_fake_models()


@pytest.fixture
def fake_models_always_loop():
    """Register a 'fake-agent' that always calls the tool and never stops.

    Used to exercise the reflection/hard-cap safety net: unlike ``fake_models``
    (which stops after one tool call), this agent would loop forever without
    the reflection/hard-cap mechanism in ``get_subgraph()``.
    """
    from fakes.fake_llm import FakeChatModel
    from model_factory import clear_fake_models, register_fake_model

    register_fake_model(
        "fake-planner",
        FakeChatModel(responses=[
            # The recon subgraph's hard-cap reflection reaches the planner as a
            # ToolMessage containing "INCONCLUSIVE" — recognize it and stop
            # dispatching, rather than looping the planner forever too.
            ("INCONCLUSIVE", "Penetration test complete.\n\n## Findings Summary\n\n"),
            (
                "",
                [{
                    "name": "recon",
                    "args": {
                        "instructions": "Scan http://fake-target.",
                        "execution_name": "Initial recon",
                    },
                }],
            ),
        ]),
    )
    register_fake_model(
        "fake-agent",
        FakeChatModel(responses=[
            # The hard-cap reflection prompt: respond with plain text (no tool
            # call), like a real tool-less reflect turn would.
            ("reached the hard limit", "Attempted repeated requests with no new signal. INCONCLUSIVE."),
            # Periodic (non-final) reflection checkpoints: also plain text.
            ("Checkpoint: you have used", "Continuing the same approach."),
            # Regression guard: if the "continue the task" nudge were ever
            # dropped from reflect_node, the last message fed back into
            # agent_node after a non-final checkpoint would be the reflection
            # reply's OWN text above, not a fresh human turn. A real model
            # asked to generate another assistant turn immediately after its
            # own prior one tends to treat the task as already resolved and
            # emits no tool call — simulate that here so this test fails loudly
            # if the nudge is ever removed, instead of the subgraph silently
            # ending early and control returning to the planner.
            ("Continuing the same approach.", ""),
            # Catch-all: always call the tool again otherwise (including on the
            # very first turn, and after the "continue the task" nudge).
            ("", [{"name": "fake_http_get", "args": {"url": "http://fake-target"}}]),
        ]),
    )
    register_fake_model(
        "fake-summarizer",
        FakeChatModel(responses=[
            (
                "",
                '{"key": "fake_http_get http://fake-target - 200 OK", "summary": "GET returned 200 OK."}',
            ),
        ]),
    )

    yield

    clear_fake_models()


@pytest.fixture
def fake_models_empty_agent_turn():
    """Register a 'fake-agent' whose very first turn returns nothing at all.

    Used to exercise the empty-turn recovery nudge in ``agent_node``
    (``subgraph.py``): a turn with no content and no tool calls would
    otherwise silently end the subgraph via ``should_continue`` before any
    work is done. The fake agent simulates exactly that failure mode, then
    recovers once the corrective nudge is injected.
    """
    from fakes.fake_llm import FakeChatModel
    from model_factory import clear_fake_models, register_fake_model

    register_fake_model(
        "fake-planner",
        FakeChatModel(responses=[
            (
                "Reconnaissance complete",
                "Penetration test complete.\n\n"
                "## Findings Summary\n\n"
                "| Endpoint | Vulnerability | PoC |\n"
                "| --- | --- | --- |\n"
                "| /login | SQL Injection | admin' OR '1'='1 |\n",
            ),
            (
                "",
                [{
                    "name": "recon",
                    "args": {
                        "instructions": "Scan http://fake-target.",
                        "execution_name": "Initial recon",
                    },
                }],
            ),
        ]),
    )
    register_fake_model(
        "fake-agent",
        FakeChatModel(responses=[
            # The nudge injected after an empty turn contains this exact
            # phrase (see agent_node in subgraph.py) — recognize it and
            # recover by calling the tool.
            (
                "no content and no tool calls",
                [{"name": "fake_http_get", "args": {"url": "http://fake-target"}}],
            ),
            ("200", "Reconnaissance complete."),
            # Catch-all: the very first turn returns nothing — no content,
            # no tool calls — simulating the model failure being guarded against.
            ("", ""),
        ]),
    )
    register_fake_model(
        "fake-summarizer",
        FakeChatModel(responses=[
            (
                "",
                '{"key": "fake_http_get http://fake-target - 200 OK", "summary": "GET returned 200 OK."}',
            ),
        ]),
    )

    yield

    clear_fake_models()


@pytest.fixture
def fake_models_textless_content_agent_turn():
    """Register a 'fake-agent' whose first turn returns a textless content list.

    Simulates the Gemini-3 failure mode that motivated ``has_usable_output``:
    a turn that spends its whole output budget on reasoning comes back with a
    *truthy but textless* content list —
    ``[{"type": "text", "text": "", "extras": {"signature": ...}}]``. A naive
    ``if response.content`` guard treats that as valid output and silently ends
    the subgraph; the nudge must instead recognise it as empty and recover.
    """
    from fakes.fake_llm import FakeChatModel
    from model_factory import clear_fake_models, register_fake_model

    register_fake_model(
        "fake-planner",
        FakeChatModel(responses=[
            (
                "Reconnaissance complete",
                "Penetration test complete.\n\n"
                "## Findings Summary\n\n"
                "| Endpoint | Vulnerability | PoC |\n"
                "| --- | --- | --- |\n"
                "| /login | SQL Injection | admin' OR '1'='1 |\n",
            ),
            (
                "",
                [{
                    "name": "recon",
                    "args": {
                        "instructions": "Scan http://fake-target.",
                        "execution_name": "Initial recon",
                    },
                }],
            ),
        ]),
    )
    register_fake_model(
        "fake-agent",
        FakeChatModel(responses=[
            (
                "no content and no tool calls",
                [{"name": "fake_http_get", "args": {"url": "http://fake-target"}}],
            ),
            ("200", "Reconnaissance complete."),
            # Catch-all first turn: a truthy-but-textless content list. Pre-fix
            # this sailed past the nudge (``bool(content)`` is True); it must
            # now be treated as empty and nudged.
            ("", [{"type": "text", "text": "", "extras": {"signature": "AY8=="}}]),
        ]),
    )
    register_fake_model(
        "fake-summarizer",
        FakeChatModel(responses=[
            (
                "",
                '{"key": "fake_http_get http://fake-target - 200 OK", "summary": "GET returned 200 OK."}',
            ),
        ]),
    )

    yield

    clear_fake_models()


@pytest.fixture
def fake_models_planner_kb_read():
    """Register a 'fake-planner' that reads the KB before dispatching any agent.

    Used to exercise the planner's read-only kb_get/kb_list_dir tools
    (main_graph.py): the planner's first turn calls ``kb_list_dir`` (routed
    through the main graph's ``kb_tools`` node), the resulting ToolMessage
    feeds back into the planner, which then dispatches ``recon`` as normal.
    """
    from fakes.fake_llm import FakeChatModel
    from model_factory import clear_fake_models, register_fake_model

    register_fake_model(
        "fake-planner",
        FakeChatModel(responses=[
            (
                "Reconnaissance complete",
                "Penetration test complete.\n\n"
                "## Findings Summary\n\n"
                "| Endpoint | Vulnerability | PoC |\n"
                "| --- | --- | --- |\n"
                "| /login | SQL Injection | admin' OR '1'='1 |\n",
            ),
            (
                # After the KB read, the root lists the seeded skills library
                # (kb_list_dir("") -> ["skills"]); recognize that and dispatch recon.
                "skills",
                [{
                    "name": "recon",
                    "args": {
                        "instructions": "Scan http://fake-target.",
                        "execution_name": "Initial recon",
                    },
                }],
            ),
            # Very first turn: read the KB (skills seeded, no findings yet) before dispatching.
            ("", [{"name": "kb_list_dir", "args": {"path": ""}}]),
        ]),
    )

    register_fake_model(
        "fake-agent",
        FakeChatModel(responses=[
            ("200", "Reconnaissance complete."),
            (
                "",
                [{"name": "fake_http_get", "args": {"url": "http://fake-target"}}],
            ),
        ]),
    )

    register_fake_model(
        "fake-summarizer",
        FakeChatModel(responses=[
            (
                "",
                '{"key": "fake_http_get http://fake-target - 200 OK", "summary": "GET returned 200 OK."}',
            ),
        ]),
    )

    yield

    clear_fake_models()


@pytest.fixture
def fake_tool_registry():
    """Inject a ``fake_http_get`` tool into the ZAP tool registry.

    The tool returns a canned JSON payload so no real ZAP proxy is needed.
    Teardown restores the original registry.
    """
    import tools.zap_tools as zt
    from langchain_core.tools import tool

    @tool
    def fake_http_get(url: str) -> dict:
        """Fake http_get tool for testing — returns a canned response."""
        return {"status": 200, "headers": {}, "body": "<html>fake</html>"}

    original = dict(zt.TOOL_REGISTRY)
    zt.TOOL_REGISTRY["fake_http_get"] = fake_http_get
    yield
    zt.TOOL_REGISTRY.clear()
    zt.TOOL_REGISTRY.update(original)


@pytest.fixture
async def api_client(tmp_path, monkeypatch):
    """Provide an httpx AsyncClient wired to the FastAPI ASGI app.

    Sets ``_runs_dir`` to a pytest-managed temp directory, resets the
    in-memory run registry between tests, and monkeypatches the ZAP
    launcher so no docker calls happen in-process.  The fake ZAP client
    returned by ``start_zap`` is never actually invoked because
    ``fake_tool_registry`` supplies test-only tool closures.
    """
    import api as api_module
    from api import app
    from run_manager import run_manager
    from tools.zap_tools import ZapClient

    monkeypatch.setattr(api_module, "_runs_dir", tmp_path)
    # Clear the run manager's in-memory state to avoid cross-test pollution.
    run_manager._runs.clear()

    # No docker in tests — replace every launcher call site imported into
    # api.py with an async no-op / fake-client stub.
    async def _fake_ensure_network() -> None:
        return None

    async def _fake_sweep_orphans() -> None:
        return None

    async def _fake_start_zap(run_id: str) -> ZapClient:
        return ZapClient(url="http://fake-zap.invalid", api_key="")

    async def _fake_stop_zap(zap: ZapClient, run_id: str) -> None:
        return None

    monkeypatch.setattr(api_module, "ensure_network", _fake_ensure_network)
    monkeypatch.setattr(api_module, "sweep_orphans", _fake_sweep_orphans)
    monkeypatch.setattr(api_module, "start_zap", _fake_start_zap)
    monkeypatch.setattr(api_module, "stop_zap", _fake_stop_zap)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


async def collect_sse_events(client: AsyncClient, run_id: str) -> list[dict]:
    """Consume the SSE stream for *run_id* and return all parsed events.

    Blocks until the server closes the stream (run completed or failed).
    """
    events: list[dict] = []
    async with client.stream("GET", f"/api/v1/runs/{run_id}/events") as resp:
        current_type: str | None = None
        async for line in resp.aiter_lines():
            if line.startswith("event:"):
                current_type = line[len("event:"):].strip()
            elif line.startswith("data:") and current_type is not None:
                events.append({
                    "type": current_type,
                    "payload": json.loads(line[len("data:"):].strip()),
                })
                current_type = None
    return events


async def start_run(client: AsyncClient) -> str:
    """POST a fake run config and return the run_id."""
    resp = await client.post("/api/v1/runs", json=FAKE_RUN_CONFIG)
    assert resp.status_code == 201, resp.text
    return resp.json()["run_id"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_all_event_types_emitted(fake_models, fake_tool_registry, api_client):
    """Every expected SSE event type must appear at least once."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)
    types = {e["type"] for e in events}

    assert "run_status" in types
    assert "planner_message" in types
    assert "subgraph_start" in types
    assert "subgraph_agent_message" in types
    assert "subgraph_tool_call" in types
    assert "subgraph_end" in types
    assert "kb_update" in types
    assert "node_start" in types
    assert "node_end" in types


async def test_run_status_lifecycle(fake_models, fake_tool_registry, api_client):
    """run_status events must show the run transitioning to running then completed."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)
    statuses = [e["payload"]["status"] for e in events if e["type"] == "run_status"]

    assert len(statuses) >= 2
    assert statuses[0] == "running"
    assert statuses[-1] == "completed"


async def test_findings_table_parsed_and_persisted(fake_models, fake_tool_registry, api_client, tmp_path):
    """The planner's findings table must be parsed and written to trace.json."""
    run_id = await start_run(api_client)
    await collect_sse_events(api_client, run_id)

    trace_path = tmp_path / run_id / "trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))

    assert trace["findings"] == [
        {"endpoint": "/login", "vulnerability": "SQL Injection", "poc": "admin' OR '1'='1"},
    ]


async def test_planner_calls_recon_agent(fake_models, fake_tool_registry, api_client):
    """The first planner_message must contain a tool call to the 'recon' agent."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    planner_msgs_with_calls = [
        e for e in events
        if e["type"] == "planner_message" and e["payload"].get("tool_calls")
    ]
    assert len(planner_msgs_with_calls) >= 1
    first_call = planner_msgs_with_calls[0]["payload"]["tool_calls"][0]
    assert first_call["agent"] == "recon"


async def test_planner_reads_kb_before_dispatch(
    fake_models_planner_kb_read, fake_tool_registry, api_client
):
    """The planner must be able to read the KB directly before dispatching an agent.

    Exercises the main graph's new ``kb_tools`` node: a planner turn that only
    calls kb_get/kb_list_dir must route there (not to an agent subgraph or the
    multi-call-reject node), emit a ``planner_kb_tool_call`` event, and loop
    back to the planner so it can still dispatch ``recon`` afterwards.
    """
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    kb_read_events = [e for e in events if e["type"] == "planner_kb_tool_call"]
    assert len(kb_read_events) == 1
    assert kb_read_events[0]["payload"]["tool_name"] == "kb_list_dir"

    # The planner still dispatches recon normally after reading the KB.
    starts = [e for e in events if e["type"] == "subgraph_start"]
    assert len(starts) >= 1
    assert starts[0]["payload"]["agent"] == "recon"

    statuses = [e["payload"]["status"] for e in events if e["type"] == "run_status"]
    assert statuses[-1] == "completed"


async def test_subgraph_start_and_end(fake_models, fake_tool_registry, api_client):
    """subgraph_start and subgraph_end events must reference the 'recon' agent."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    starts = [e for e in events if e["type"] == "subgraph_start"]
    ends = [e for e in events if e["type"] == "subgraph_end"]

    assert len(starts) >= 1
    assert starts[0]["payload"]["agent"] == "recon"
    assert starts[0]["payload"]["execution_name"] == "Initial recon"
    assert len(ends) >= 1
    assert ends[0]["payload"]["agent"] == "recon"
    assert ends[0]["payload"]["execution_name"] == "Initial recon"


async def test_subgraph_tool_call_payload(fake_models, fake_tool_registry, api_client):
    """subgraph_tool_call must identify the tool, carry a summary, and a KB key."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    tool_events = [e for e in events if e["type"] == "subgraph_tool_call"]
    assert len(tool_events) == 1

    payload = tool_events[0]["payload"]
    assert payload["tool_name"] == "fake_http_get"
    assert payload["agent"] == "recon"
    assert payload["execution_name"] == "Initial recon"
    assert payload["summary"]
    assert payload["kb_key"]
    assert payload["kb_key"].startswith("recon/initial_recon/tool_logs/")
    assert payload["raw_output"]


async def test_kb_update_fires_after_tool_call(fake_models, fake_tool_registry, api_client):
    """kb_update must fire at least once with a non-empty keys list."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    kb_updates = [e for e in events if e["type"] == "kb_update"]
    assert len(kb_updates) >= 1
    assert len(kb_updates[0]["payload"]["keys"]) > 0


async def test_subgraph_agent_messages_present(fake_models, fake_tool_registry, api_client):
    """At least two subgraph_agent_message events must fire: one with a tool call,
    one with a final text response."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    agent_msgs = [e for e in events if e["type"] == "subgraph_agent_message"]
    assert len(agent_msgs) >= 2

    msgs_with_tool_calls = [e for e in agent_msgs if e["payload"].get("tool_calls")]
    msgs_with_content = [e for e in agent_msgs if e["payload"].get("content")]
    assert len(msgs_with_tool_calls) >= 1
    assert len(msgs_with_content) >= 1


async def test_run_id_present_in_every_event(fake_models, fake_tool_registry, api_client):
    """Every SSE event payload must carry the run_id."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    assert events, "No events received"
    for event in events:
        assert event["payload"].get("run_id") == run_id, (
            f"Event '{event['type']}' is missing run_id: {event['payload']}"
        )


async def test_reconnect_replays_all_stored_events(fake_models, fake_tool_registry, api_client):
    """Connecting to a completed run's SSE stream a second time must replay
    all stored events in the same order (tokens excluded, which are never stored)."""
    run_id = await start_run(api_client)
    first = await collect_sse_events(api_client, run_id)
    second = await collect_sse_events(api_client, run_id)

    assert first, "First connection received no events"
    assert [e["type"] for e in first] == [e["type"] for e in second]
    assert [e["payload"] for e in first] == [e["payload"] for e in second]


async def test_node_start_end_pairs(fake_models, fake_tool_registry, api_client):
    """Every node_start must have a corresponding node_end for the same agent/node."""
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    starts = [(e["payload"]["agent"], e["payload"]["node"]) for e in events if e["type"] == "node_start"]
    ends = [(e["payload"]["agent"], e["payload"]["node"]) for e in events if e["type"] == "node_end"]

    # Every (agent, node) pair that started must also end.
    for pair in starts:
        assert pair in ends, f"node_start for {pair} has no matching node_end"


async def test_reflection_checkpoint_and_hard_cap_stop_infinite_loop(
    fake_models_always_loop, fake_tool_registry, api_client
):
    """An agent that always calls a tool must be stopped by the reflection/hard-cap
    safety net rather than looping forever.

    With ``reflection_interval=2`` and ``max_tool_calls=5`` (configured on the
    'recon' agent in FAKE_RUN_CONFIG) and a fake agent model that unconditionally
    re-issues the same tool call every turn, checkpoints must fire at tool-call
    counts 2 and 4, and the subgraph must end right after the hard-cap checkpoint
    at count 5 — never running away.
    """
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    agent_msgs = [e for e in events if e["type"] == "subgraph_agent_message"]
    reflections = [e for e in events if e["type"] == "subgraph_reflection"]
    ends = [e for e in events if e["type"] == "subgraph_end"]

    # Exactly 5 agent turns, each with a tool call (the fake agent never stops on its own).
    assert len(agent_msgs) == 5
    assert all(m["payload"]["tool_calls"] for m in agent_msgs)

    # Reflection fires at count=2, count=4, and the final hard-cap checkpoint at count=5.
    assert len(reflections) == 3
    for r in reflections:
        assert r["payload"]["agent"] == "recon"

    # The subgraph must actually terminate (not hang/crash the run) right after the
    # hard cap is reached — not run away past 5 tool calls.
    assert len(ends) == 1
    assert ends[0]["payload"]["agent"] == "recon"

    statuses = [e["payload"]["status"] for e in events if e["type"] == "run_status"]
    assert statuses[-1] == "completed"


async def test_empty_agent_turn_recovers_via_nudge(
    fake_models_empty_agent_turn, fake_tool_registry, api_client
):
    """An agent turn with no content and no tool calls must be nudged to
    retry instead of silently ending the subgraph with no work done.

    The fake agent's first turn returns nothing at all; ``agent_node``
    must inject a corrective HumanMessage and re-invoke the LLM, which
    then recovers by calling the tool and completing normally.
    """
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    agent_msgs = [e for e in events if e["type"] == "subgraph_agent_message"]

    # Turn 1: the simulated empty failure (visible in the event stream, not swallowed).
    assert agent_msgs[0]["payload"]["content"] == ""
    assert agent_msgs[0]["payload"]["tool_calls"] == []
    # Turn 2: recovered after the nudge, issuing the tool call.
    assert agent_msgs[1]["payload"]["tool_calls"]
    # Turn 3: final wrap-up after the tool result comes back.
    assert agent_msgs[2]["payload"]["content"] == "Reconnaissance complete."

    assert any(e["type"] == "subgraph_tool_call" for e in events)
    ends = [e for e in events if e["type"] == "subgraph_end"]
    assert len(ends) == 1

    statuses = [e["payload"]["status"] for e in events if e["type"] == "run_status"]
    assert statuses[-1] == "completed"


async def test_textless_reasoning_turn_recovers_via_nudge(
    fake_models_textless_content_agent_turn, fake_tool_registry, api_client
):
    """A turn with a truthy-but-textless content list must be nudged, not accepted.

    Regression guard for the Gemini-3 ``MAX_TOKENS``-during-reasoning bug: the
    turn returns ``[{"type": "text", "text": "", "extras": {...}}]`` — a
    non-empty (truthy) list with no usable text and no tool call. The old
    ``if response.content`` guard treated it as valid output and ended the
    subgraph with no work done; ``has_usable_output`` must catch it so the
    nudge fires and the agent recovers.
    """
    run_id = await start_run(api_client)
    events = await collect_sse_events(api_client, run_id)

    agent_msgs = [e for e in events if e["type"] == "subgraph_agent_message"]

    # Turn 1: textless content extracts to "" and carries no tool call — the
    # simulated empty failure, surfaced (not swallowed) in the event stream.
    assert agent_msgs[0]["payload"]["content"] == ""
    assert agent_msgs[0]["payload"]["tool_calls"] == []
    # Turn 2: recovered after the nudge, issuing the tool call (this row would
    # not exist pre-fix — the subgraph would have ended after turn 1).
    assert agent_msgs[1]["payload"]["tool_calls"]
    # Turn 3: final wrap-up after the tool result comes back.
    assert agent_msgs[2]["payload"]["content"] == "Reconnaissance complete."

    assert any(e["type"] == "subgraph_tool_call" for e in events)
    statuses = [e["payload"]["status"] for e in events if e["type"] == "run_status"]
    assert statuses[-1] == "completed"
