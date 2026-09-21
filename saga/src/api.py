"""FastAPI application for SagaPT.

Exposes run lifecycle, SSE event streaming, knowledge base queries, and the
Mermaid graph diagram. Start with ``uvicorn api:app`` or via ``saga serve``.
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Must run before any project import — several read env vars at module import
# time (e.g. tools/zap_tools.py's ZAP_URL). Idempotent with main.py's own call;
# needed here too since this module can be started directly via `uvicorn api:app`.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_REPO_ROOT / "saga.env")
load_dotenv(_REPO_ROOT / "saga.secrets.env")

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from run_manager import (
    RunState,
    RunStatus,
    TERMINAL_STATUSES,
    build_initial_state,
    run_manager,
    stream_run,
)
from runner import build_graph, read_config
from tools.zap_launcher import ensure_network, start_zap, stop_zap, sweep_orphans

logger = logging.getLogger(__name__)

# Runs persistence directory — set during lifespan startup.
_runs_dir: Path = Path("./saga_runs")

# Cached Mermaid diagram — built once on first request to avoid rebuilding the
# graph on every call (graph construction loads models and reads config).
_mermaid_cache: str | None = None

# Semaphore capping concurrent live runs.  Populated by lifespan on the API
# server's normal startup path; ``_get_run_slots()`` lazily creates it on
# first use for callers that bypass lifespan (e.g. ASGI-transport tests
# instantiate the app without running lifespan events).
_run_slots: asyncio.Semaphore | None = None


def _get_run_slots() -> asyncio.Semaphore:
    """Return the run-slot semaphore, creating it lazily if lifespan didn't."""
    global _run_slots
    if _run_slots is None:
        max_concurrent = int(os.getenv("SAGA_MAX_CONCURRENT_RUNS", "4"))
        _run_slots = asyncio.Semaphore(max_concurrent)
        logger.debug("Run-slot semaphore lazy-initialised (max = %d).", max_concurrent)
    return _run_slots


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load persisted runs, sweep orphan ZAP containers, and build the run-slot semaphore."""
    global _runs_dir
    _runs_dir = Path(os.getenv("SAGA_RUNS_DIR", "./saga_runs"))
    _runs_dir.mkdir(parents=True, exist_ok=True)
    run_manager.load_persisted_runs(_runs_dir)

    # Materialise the semaphore up-front so its size is logged and its loop is
    # the same one lifespan runs on.  (_get_run_slots also lazy-inits for
    # ASGI-transport tests that skip lifespan entirely.)
    _get_run_slots()

    try:
        await ensure_network()
        await sweep_orphans()
    except Exception:
        # Best-effort — a failure here shouldn't block startup (e.g. docker
        # daemon not running on a config-only server).
        logger.exception("ZAP infra bootstrap (ensure_network/sweep_orphans) failed; continuing.")

    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


app = FastAPI(
    title="SagaPT API",
    description="Web security penetration testing automation — run control and observability.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------


class RunSummary(BaseModel):
    """Lightweight run metadata returned from list/create/status endpoints."""

    run_id: str
    name: str
    status: RunStatus
    target: str
    started_at: datetime
    ended_at: datetime | None
    error: str | None


class KBKeysResponse(BaseModel):
    run_id: str
    keys: list[str]


class KBEntryResponse(BaseModel):
    run_id: str
    key: str
    value: str


class KBDirResponse(BaseModel):
    run_id: str
    path: str
    entries: list[str]


class MermaidResponse(BaseModel):
    mermaid: str


# ---------------------------------------------------------------------------
# Run configuration request models (mirror saga.toml structure)
# ---------------------------------------------------------------------------


class _PromptsConfig(BaseModel):
    system: str
    human: str


class _ModelConfig(BaseModel):
    model_provider: str
    model_name: str
    temperature: float = 0.0
    model_kwargs: dict[str, Any] = {}
    """Provider-specific kwargs passed straight through to the underlying
    LangChain chat model (e.g. ``{"thinking_level": "low"}`` for Gemini 3+
    via the ``google`` provider). See ``model_factory.ModelParameters``."""


class _ToolConfig(BaseModel):
    """Per-tool configuration inside an agent's ``tools`` list."""
    name: str
    summarize: bool = False


class _AgentRunConfig(_ModelConfig):
    name: str
    description: str
    tools: list[str | _ToolConfig]
    prompts: _PromptsConfig
    reflection_interval: int = 8
    """Force a tool-less reflection turn every this many tool-call turns."""
    max_tool_calls: int = 28
    """Hard cap on tool-call turns per invocation; ends the subgraph after one
    final reflection turn once reached."""


class _SummarizerRunConfig(_ModelConfig):
    prompts: _PromptsConfig


class _PlannerRunConfig(_ModelConfig):
    prompts: _PromptsConfig


class _GeneralRunConfig(BaseModel):
    target: str
    run_timeout_s: int | None = None
    """Wall-clock cap in seconds for the entire graph execution.

    ``None`` or ``<= 0`` means unlimited (preserves pre-existing behaviour).
    Enforced by wrapping ``stream_run`` in ``asyncio.wait_for`` inside
    ``_build_and_stream`` — a timeout aborts with FAILED status and a clear
    error message. Long-running benchmarks that would otherwise burn tokens
    forever in a fail case get bounded here.
    """
    token_budget: int | None = None
    """Cumulative token cap across every AI event in the run.

    ``None`` or ``<= 0`` means unlimited. Checked at every
    ``_extract_usage`` site in ``run_manager.stream_run``; crossing the
    threshold raises :class:`run_manager.TokenBudgetExceeded`, translated
    into FAILED status with a diagnostic error message.
    """


class _ZapRunConfig(BaseModel):
    context_name: str = "sagapt"
    include: list[str] = []
    exclude: list[str] = []
    spider_exclude: list[str] = []


class TargetProfile(BaseModel):
    """A named, selectable target (mirrors a ``[targets.<key>]`` table in saga.toml)."""

    key: str
    label: str
    target: str
    zap: _ZapRunConfig
    human_prompt: str | None = None


class RunConfig(BaseModel):
    """Full run configuration, mirroring the ``saga.toml`` structure.

    Pass this as the JSON body to ``POST /api/v1/runs`` to start a run with
    a specific configuration rather than the file-based default.
    """

    general: _GeneralRunConfig
    summarizer: _SummarizerRunConfig
    planner: _PlannerRunConfig
    agents: dict[str, _AgentRunConfig]
    zap: _ZapRunConfig | None = None
    name: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_summary(run: RunState) -> RunSummary:
    """Convert a RunState to a RunSummary response model."""
    return RunSummary(
        run_id=run.run_id,
        name=run.name,
        status=run.status,
        target=run.target,
        started_at=run.started_at,
        ended_at=run.ended_at,
        error=run.error,
    )


def _get_run_or_404(run_id: str) -> RunState:
    run = run_manager.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return run


# ---------------------------------------------------------------------------
# Run lifecycle
# ---------------------------------------------------------------------------


@app.post("/api/v1/runs", response_model=RunSummary, status_code=status.HTTP_201_CREATED)
async def create_run(body: RunConfig) -> RunSummary:
    """Start a new penetration testing run.

    Accepts a full :class:`RunConfig` body (mirrors ``saga.toml`` structure)
    and returns immediately with the new ``run_id`` in PENDING state.
    Graph construction and execution run in the background so the endpoint
    never blocks (model loading can take 30+ s).
    """
    config = body.model_dump()
    target: str = config["general"]["target"]
    agent_names = frozenset(config["agents"].keys())

    run_id, default_name = run_manager.next_run_id_and_name()
    name = body.name or default_name
    run = run_manager.create_run(run_id=run_id, name=name, kb=None, target=target)
    # Snapshot per-agent limits at run start (keyed by graph-node name, e.g.
    # "recon_agent") so the CSV export can detect hard-cap hits even if
    # saga.toml/this run's config changes later.
    run.agent_config = {
        cfg["name"]: {
            "max_tool_calls": cfg.get("max_tool_calls", 28),
            "reflection_interval": cfg.get("reflection_interval", 8),
            "model_name": cfg.get("model_name"),
        }
        for cfg in config["agents"].values()
    }

    run_timeout_s = config["general"].get("run_timeout_s")
    token_budget = config["general"].get("token_budget")

    async def _build_and_stream() -> None:
        # Wait for a free run slot, then acquire a per-run ZAP container. Both
        # steps happen while the run is still PENDING so the frontend/CLI sees
        # queued runs sit visibly at the front of the list until infra frees.
        try:
            async with _get_run_slots():
                zap = await start_zap(run_id)
                try:
                    # build_graph() is synchronous and may do slow I/O
                    # (ZAP context setup, model checks). Run in a thread so
                    # the event loop stays responsive.
                    graph, planner_cfg, _target, kb = await asyncio.to_thread(
                        build_graph, config, zap, run_id=run_id
                    )
                    # Wire up write-through KB persistence before execution
                    # starts so every kb.store() call is immediately written.
                    run_dir = _runs_dir / run_id
                    run_dir.mkdir(parents=True, exist_ok=True)
                    kb.set_root(run_dir / "knowledge_base")
                    run.kb = kb
                    initial_state = build_initial_state(planner_cfg, _target)
                    # Wall-clock cap enforced here; token cap enforced inside
                    # stream_run at each usage-metadata event.  ``None`` /
                    # ``<= 0`` disables the wall-clock cap (asyncio.wait_for
                    # with timeout=None waits forever).
                    effective_timeout = (
                        run_timeout_s if run_timeout_s and run_timeout_s > 0 else None
                    )
                    try:
                        await asyncio.wait_for(
                            stream_run(
                                run, graph, initial_state, agent_names,
                                _runs_dir, token_budget=token_budget,
                            ),
                            timeout=effective_timeout,
                        )
                    except asyncio.TimeoutError:
                        # stream_run's own CancelledError handler fires as
                        # wait_for cancels the task, so run.status is already
                        # CANCELLED and cleanup (persist, close_broadcast,
                        # ZAP teardown via the outer finally) is done. Only
                        # need to re-label it as a timeout FAILED so the
                        # error message is diagnostic rather than a bare
                        # "cancelled".
                        run.status = RunStatus.FAILED
                        run.error = f"Timeout: exceeded {effective_timeout}s wall-clock limit"
                        logger.warning("Run %s hit wall-clock timeout (%ss).", run_id, effective_timeout)
                        _status_payload = {"run_id": run_id, "status": run.status, "error": run.error}
                        run_manager.broadcast(run_id, "run_status", _status_payload)
                        run_manager.broadcast_global("run_status", _status_payload)
                finally:
                    await stop_zap(zap, run_id)
        except Exception as exc:
            # A failure here (bad config, prompt formatting error, ZAP
            # startup failure, docker daemon down, ...) happens either
            # before stream_run has run at all or after it aborted. Either
            # way, without this handler the background task's exception
            # would never surface (run._task holds a strong reference, so
            # asyncio never logs "exception was never retrieved" and the
            # run is stuck showing PENDING/RUNNING forever).
            if run.status not in TERMINAL_STATUSES:
                run.status = RunStatus.FAILED
                run.ended_at = datetime.now(timezone.utc)
                run.error = str(exc)
            logger.exception("Run %s failed before/around execution: %s", run_id, exc)
            run_manager.broadcast(
                run_id, "error", {"run_id": run_id, "message": str(exc)}
            )
            _status_payload = {"run_id": run_id, "status": run.status, "error": run.error}
            run_manager.broadcast(run_id, "run_status", _status_payload)
            run_manager.broadcast_global("run_status", _status_payload)
            run_manager.close_broadcast(run_id)

    task = asyncio.create_task(_build_and_stream())
    run._task = task

    # Notify global subscribers so other tabs / dashboards see the new run
    # appear without polling. Sent AFTER _task is attached so cancel/delete
    # from another client can operate on the task immediately.
    run_manager.broadcast_global("run_created", _run_summary(run).model_dump(mode="json"))

    logger.info("Queued run %s against %s.", run_id, target)
    return _run_summary(run)


@app.post("/api/v1/runs/{run_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_run(run_id: str) -> None:
    """Cancel a running or pending run without deleting it.

    Idempotent — cancelling a run that is already in a terminal state is a
    no-op. The eventual ``run_status`` event carries the CANCELLED status.
    """
    run = _get_run_or_404(run_id)
    if run._task and not run._task.done():
        run._task.cancel()


@app.get("/api/v1/runs", response_model=list[RunSummary])
async def list_runs() -> list[RunSummary]:
    """List all runs (past and present), including runs loaded from disk on startup."""
    return [_run_summary(r) for r in run_manager.list_runs()]


@app.get("/api/v1/runs/{run_id}", response_model=RunSummary)
async def get_run(run_id: str) -> RunSummary:
    """Return the current status of a specific run."""
    return _run_summary(_get_run_or_404(run_id))


@app.delete("/api/v1/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_run(run_id: str) -> None:
    """Permanently delete a run.

    Cancels the run if it is still in progress, removes it from the
    in-memory registry, and deletes its directory from disk.
    """
    _get_run_or_404(run_id)
    run_manager.delete_run(run_id, _runs_dir)
    run_manager.broadcast_global("run_deleted", {"run_id": run_id})


# ---------------------------------------------------------------------------
# SSE event stream
# ---------------------------------------------------------------------------


@app.get("/api/v1/runs/{run_id}/events")
async def run_events(run_id: str, request: Request) -> EventSourceResponse:
    """Stream graph execution events as Server-Sent Events.

    Each event has a named ``event:`` type and a JSON ``data:`` payload.

    **Event types emitted:**
    - ``run_status`` — run lifecycle change (pending/running/completed/failed/cancelled)
    - ``planner_message`` — planner LLM response (reasoning, content, tool_calls)
    - ``subgraph_start`` — subgraph agent begins (agent, instructions)
    - ``subgraph_agent_message`` — agent LLM response (reasoning, content, tool_calls)
    - ``subgraph_reflection`` — forced tool-less checkpoint turn (reasoning, content)
    - ``subgraph_tool_call`` — ZAP tool executed and summarised (args, raw_output, summary)
    - ``subgraph_kb_tool_call`` — KB tool executed (tool_name, tool_args, result)
    - ``subgraph_end`` — subgraph agent finished (agent, result)
    - ``node_start`` / ``node_end`` — graph node lifecycle for visualisation
    - ``kb_update`` — knowledge base keys changed
    - ``token`` — incremental LLM token (live stream only; not replayed on reconnect)
    - ``error`` — unhandled exception during execution

    **Reconnect behaviour:** If a client reconnects to an in-progress run, all
    stored events emitted so far (excluding tokens) are replayed immediately,
    followed by the live stream. For finished runs, all stored events are
    replayed and the stream closes.
    """
    run = _get_run_or_404(run_id)

    async def event_generator() -> Any:
        if run.status in TERMINAL_STATUSES:
            # Finished run: replay all stored events then close.
            for ev in run_manager.load_run_events(run_id):
                yield ServerSentEvent(
                    data=json.dumps(ev["payload"]),
                    event=ev["type"],
                )
            return

        # In-progress run: snapshot stored events and subscribe atomically.
        # There is no await between these two operations, so no events can be
        # missed — new events go both to the queue and stored_events in order.
        snapshot = list(run.stored_events)
        q = run_manager.subscribe(run_id)

        try:
            # Replay events that arrived before this client connected.
            for ev in snapshot:
                yield ServerSentEvent(
                    data=json.dumps(ev["payload"]),
                    event=ev["type"],
                )
            # Live stream.
            while True:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(q.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                if item is None:
                    break
                yield item
        except (asyncio.CancelledError, GeneratorExit):
            pass
        finally:
            run_manager.unsubscribe(run_id, q)
            # NOTE: we intentionally do NOT cancel the background task when the
            # SSE client disconnects. Runs are cancelled via the dedicated
            # POST /api/v1/runs/{run_id}/cancel endpoint so switching tabs or
            # closing the browser doesn't kill an in-progress run.

    return EventSourceResponse(event_generator())


@app.get("/api/v1/events")
async def global_events(request: Request) -> EventSourceResponse:
    """Global lifecycle stream for all runs.

    Emits ``run_created`` / ``run_status`` / ``run_deleted`` events so other
    tabs and dashboards see runs appear and change state without polling. The
    stream stays open indefinitely; keepalive comments are sent every 15 s.
    """
    q = run_manager.global_subscribe()

    async def event_generator() -> Any:
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(q.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                if item is None:
                    break
                yield item
        except (asyncio.CancelledError, GeneratorExit):
            pass
        finally:
            run_manager.global_unsubscribe(q)

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------


def _kb_root(run_id: str) -> Path:
    """Return the knowledge base root directory for *run_id*."""
    return _runs_dir / run_id / "knowledge_base"


def _load_kb_from_disk(run_id: str) -> dict[str, str]:
    """Load all KB files from ``{_runs_dir}/{run_id}/knowledge_base/``.

    Walks the directory tree and returns a ``{relative_path: content}`` dict.
    Returns an empty dict if the directory does not exist.
    """
    root = _kb_root(run_id)
    if not root.is_dir():
        return {}
    result: dict[str, str] = {}
    for file_path in root.rglob("*"):
        if file_path.is_file():
            rel = file_path.relative_to(root).as_posix()
            result[rel] = file_path.read_text(encoding="utf-8")
    return result


def _list_kb_dir_from_disk(run_id: str, path: str) -> list[str]:
    """List entries directly under *path* in the on-disk KB for *run_id*.

    Path traversal attempts are silently treated as empty results.
    """
    root = _kb_root(run_id)
    if not root.is_dir():
        return []
    target = (root / path).resolve() if path and path != "." else root.resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return []
    if not target.is_dir():
        return []
    return sorted(entry.name for entry in target.iterdir())


@app.get("/api/v1/runs/{run_id}/kb/keys", response_model=KBKeysResponse)
async def kb_keys(run_id: str) -> KBKeysResponse:
    """List all knowledge base file paths for a run (flat, recursive)."""
    run = _get_run_or_404(run_id)
    if run.kb is not None:
        keys = run.kb.list_keys()
    else:
        keys = list(_load_kb_from_disk(run_id).keys())
    return KBKeysResponse(run_id=run_id, keys=keys)


@app.get("/api/v1/runs/{run_id}/kb/dir", response_model=KBDirResponse)
async def kb_dir(run_id: str, path: str = "") -> KBDirResponse:
    """List entries directly under a knowledge base directory.

    Pass ``?path=recon/initial_recon/tool_logs`` to list a subdirectory; omit
    or pass ``""`` to list the root.
    """
    run = _get_run_or_404(run_id)
    if run.kb is not None:
        entries = run.kb.list_dir(path)
    else:
        entries = _list_kb_dir_from_disk(run_id, path)
    return KBDirResponse(run_id=run_id, path=path, entries=entries)


@app.get("/api/v1/runs/{run_id}/kb/entries/{key:path}", response_model=KBEntryResponse)
async def kb_entry(run_id: str, key: str) -> KBEntryResponse:
    """Retrieve a knowledge base file by its path.

    The ``{key:path}`` route pattern allows slashes in the path, e.g.
    ``/kb/entries/recon/initial_recon/tool_logs/get_login.md``.
    """
    run = _get_run_or_404(run_id)
    if run.kb is not None:
        value: str | None = run.kb.get(key)
    else:
        value = _load_kb_from_disk(run_id).get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"'{key}' not found in KB.")
    return KBEntryResponse(run_id=run_id, key=key, value=value)



# ---------------------------------------------------------------------------
# Graph structure
# ---------------------------------------------------------------------------


@app.get("/api/v1/config", response_model=RunConfig)
async def get_default_config() -> RunConfig:
    """Return the default run configuration read from saga.toml."""
    config = await asyncio.to_thread(read_config)
    return RunConfig.model_validate(config)


@app.get("/api/v1/targets", response_model=list[TargetProfile])
async def list_targets() -> list[TargetProfile]:
    """Return the named target profiles declared under ``[targets.*]`` in saga.toml."""
    config = await asyncio.to_thread(read_config)
    return [
        TargetProfile(
            key=key,
            label=t.get("label", key),
            target=t["target"],
            zap=_ZapRunConfig(
                include=t.get("zap_include", []),
                exclude=t.get("zap_exclude", []),
                spider_exclude=t.get("zap_spider_exclude", []),
            ),
            human_prompt=t.get("human_prompt"),
        )
        for key, t in config.get("targets", {}).items()
    ]


@app.get("/api/v1/graph/mermaid", response_model=MermaidResponse)
async def graph_mermaid() -> MermaidResponse:
    """Return the Mermaid diagram of the agent graph.

    The result is cached after the first call — graph construction is
    moderately expensive and the diagram is static.
    """
    global _mermaid_cache
    if _mermaid_cache is None:
        config = read_config()
        # zap=None → structure-only build: no live ZAP call, no container spawn.
        graph, _, _, _ = await asyncio.to_thread(build_graph, config, None)
        _mermaid_cache = graph.get_graph(xray=True).draw_mermaid()
        logger.info("Mermaid graph diagram cached.")
    return MermaidResponse(mermaid=_mermaid_cache)
