import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Must run before any project import (several read env vars at module import
# time, e.g. tools/zap_tools.py's ZAP_URL). Docker previously supplied these
# via env_file:; running natively, we load them ourselves. override=False (the
# default) so a developer's real shell env always wins over the committed files.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_REPO_ROOT / "saga.env")
load_dotenv(_REPO_ROOT / "saga.secrets.env")

from langchain_core.prompts import ChatPromptTemplate

from runner import build_graph, dict_to_tuple_list, read_config
from tools.zap_launcher import ensure_network, start_zap, stop_zap


def setup_logging() -> None:
    """Centralized logging configuration.

    Sets the root logger to WARNING to suppress noisy third-party libraries,
    then sets all SagaPT-specific loggers to the level given by the LOG_LEVEL
    environment variable (default: DEBUG).

    Uvicorn/server access logs are controlled separately by SERVER_LOG_LEVEL
    (default: WARNING, which suppresses HTTP access lines). Set it to INFO to
    re-enable them, using the same format as the rest of the logs.
    """
    saga_level_name = os.getenv("LOG_LEVEL", "DEBUG").upper()
    saga_level = getattr(logging, saga_level_name, logging.DEBUG)

    server_level_name = os.getenv("SERVER_LOG_LEVEL", "WARNING").upper()
    server_level = getattr(logging, server_level_name, logging.WARNING)

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    for name in (
        "__main__",
        "runner",
        "model_factory",
        "graph.main_graph",
        "graph.subgraph",
        "tools.zap_tools",
        "tools.kb_tools",
        "knowledge_base",
        "api",
        "run_manager",
        "export_stats",
    ):
        logging.getLogger(name).setLevel(saga_level)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).setLevel(server_level)


async def cmd_run() -> None:
    """Execute the full penetration testing workflow.

    Spawns an ephemeral ZAP container for the duration of the run and tears it
    down afterwards — mirrors the API server's per-run ZAP lifecycle so the
    CLI dev loop uses the same code path.
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting SAGA Agent...")

    config = read_config()
    logger.info("Configuration loaded from saga.toml.")
    logger.debug("Raw config keys: %s", list(config.keys()))

    # Per-invocation run id — the CLI doesn't persist runs, but this label
    # names the ZAP container and disambiguates concurrent CLI invocations.
    from datetime import datetime, timezone
    run_id = f"cli-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    await ensure_network()
    zap = await start_zap(run_id)
    try:
        main_graph, planner_cfg, target, _kb = build_graph(config, zap, run_id=run_id)

        initial_state = {
            "target": target,
            "messages": ChatPromptTemplate(
                dict_to_tuple_list(planner_cfg["prompts"])
            ).format_messages(target=target),
        }
        logger.debug(
            "Initial state prepared with %d message(s).", len(initial_state["messages"])
        )

        logger.info("Streaming main graph...")
        async for _ns, _chunk in main_graph.astream(
            initial_state, {"recursion_limit": 200}, subgraphs=True
        ):
            pass

        logger.info("Workflow complete.")
    finally:
        await stop_zap(zap, run_id)


def cmd_graph() -> None:
    """Print the ASCII and Mermaid representations of the main graph to stdout."""
    logger = logging.getLogger(__name__)
    logger.info("Generating graph diagrams...")

    config = read_config()
    # zap=None → structure-only build; no ZAP container is spawned for this
    # read-only diagram command.
    main_graph, _, _, _ = build_graph(config, None)

    graph = main_graph.get_graph(xray=True)
    print(graph.draw_ascii())
    print(graph.draw_mermaid())


def cmd_serve(host: str, port: int) -> None:
    """Start the FastAPI server with uvicorn."""
    import uvicorn

    # log_config=None prevents uvicorn from overriding the format set in setup_logging().
    uvicorn.run("api:app", host=host, port=port, reload=False, log_config=None)


def cmd_export(
    run_id: str | None, all_runs: bool, out: str | None, runs_dir: str | None = None
) -> None:
    """Export one or all persisted runs' trace.json to CSVs for offline analysis.

    Reads directly from ``{runs_dir}/{run_id}/trace.json`` — no API server or
    live infrastructure required. ``trace.json`` only exists for runs started
    via the API (``serve``/frontend), not the ``run`` command.

    ``runs_dir`` (the ``--runs-dir`` flag) selects the directory holding the run
    subdirectories, so an alternate set such as ``saga_runs_sample`` can be
    exported (with ``--all``, its combined ``export/`` is written inside it);
    it defaults to ``$SAGA_RUNS_DIR`` or ``./saga_runs``.
    """
    import export_stats

    logger = logging.getLogger(__name__)
    runs_dir = Path(runs_dir) if runs_dir else Path(os.getenv("SAGA_RUNS_DIR", "./saga_runs"))

    if all_runs:
        out_dir = Path(out) if out else runs_dir / "export"
        result = export_stats.export_all(runs_dir, out_dir)
        logger.info("Exported all runs under %s to %s.", runs_dir, result)
        print(f"Exported all runs to {result}")
        return

    if not run_id:
        print("error: provide a run_id, or use --all to export every run.", file=sys.stderr)
        sys.exit(1)

    run_dir = runs_dir / run_id
    if not (run_dir / "trace.json").exists():
        print(f"error: no trace.json found for run '{run_id}' under {runs_dir}.", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(out) if out else None
    result = export_stats.export_run(run_dir, out_dir)
    logger.info("Exported run %s to %s.", run_id, result)
    print(f"Exported run {run_id} to {result}")


def cmd_replicate(args: argparse.Namespace) -> None:
    """Dispatch ``saga replicate`` — launch the same run config N times, sequentially.

    Talks to an already-running API server over HTTP (``just serve``); does
    not build a graph or touch ZAP directly itself.
    """
    from replicate_runs import run_replication

    run_replication(
        start=args.start,
        end=args.end,
        name=args.name,
        api_base=args.api,
        poll_interval=args.poll_interval,
        reset_container=args.reset_container,
        reset_timeout=args.reset_timeout,
    )


def make_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="saga",
        description="SagaPT — LLM-driven web penetration testing automation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "commands:\n"
            "  run     Run the penetration testing workflow against the configured target.\n"
            "  graph   Print the ASCII and Mermaid diagrams of the agent graph to stdout.\n"
            "  serve   Start the FastAPI server.\n"
            "  export  Export a run's trace.json to CSVs for offline statistical analysis.\n"
            "  replicate  Launch the same run config N times, sequentially, for replicability.\n"
            "\n"
            "examples:\n"
            "  just up run\n"
            "  just up graph\n"
            "  python src/main.py serve --port 8080\n"
            "  just up export 20260713-1302-0070\n"
            "  just up export --all\n"
            "  python src/main.py replicate --start 1 --end 10 --name SQLi\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run", help="Run the penetration testing workflow.")
    subparsers.add_parser("graph", help="Print the ASCII and Mermaid graph diagrams.")
    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI API server.")
    serve_parser.add_argument(
        "--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)."
    )
    serve_parser.add_argument(
        "--port", type=int, default=8080, help="Bind port (default: 8080)."
    )
    export_parser = subparsers.add_parser(
        "export", help="Export a run's trace.json to CSVs for offline analysis."
    )
    export_parser.add_argument(
        "run_id", nargs="?", default=None, help="Run ID to export (a saga_runs/ subdirectory name)."
    )
    export_parser.add_argument(
        "--all", action="store_true", help="Export every persisted run plus combined cross-run CSVs."
    )
    export_parser.add_argument(
        "--out", default=None, help="Override the output directory (default: alongside the run's trace.json)."
    )
    export_parser.add_argument(
        "--runs-dir",
        default=None,
        help="Directory holding the persisted run subdirectories "
        "(default: $SAGA_RUNS_DIR or ./saga_runs), e.g. saga_runs_sample. "
        "With --all, the combined export/ is written inside it.",
    )

    replicate_parser = subparsers.add_parser(
        "replicate", help="Launch the same run configuration N times, sequentially, for replicability."
    )
    replicate_parser.add_argument("--start", type=int, required=True, help="First run number (inclusive).")
    replicate_parser.add_argument("--end", type=int, required=True, help="Last run number (inclusive).")
    replicate_parser.add_argument("--name", required=True, help="Base run name; runs are named '<name> #<n>'.")
    replicate_parser.add_argument("--api", default="http://127.0.0.1:8080", help="API server base URL.")
    replicate_parser.add_argument("--poll-interval", type=float, default=10, help="Seconds between run-status polls (default: 10).")
    replicate_parser.add_argument(
        "--reset-container", default=None,
        help="Docker container to restart (and wait healthy) before every run, e.g. hackergram_target. Omit to skip resetting.",
    )
    replicate_parser.add_argument(
        "--reset-timeout", type=float, default=120,
        help="Seconds to wait for --reset-container to report healthy after restart (default: 120).",
    )
    return parser


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    setup_logging()

    if args.command == "run":
        asyncio.run(cmd_run())
    elif args.command == "graph":
        cmd_graph()
    elif args.command == "serve":
        cmd_serve(host=args.host, port=args.port)
    elif args.command == "export":
        cmd_export(run_id=args.run_id, all_runs=args.all, out=args.out, runs_dir=args.runs_dir)
    elif args.command == "replicate":
        cmd_replicate(args)
