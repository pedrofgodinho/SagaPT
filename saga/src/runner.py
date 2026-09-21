"""Core application logic for SagaPT.

This module is intentionally free of CLI concerns so it can be imported
cleanly by both the CLI entry point (main.py) and a future API layer.
"""

import logging
import tomllib
from pathlib import Path

import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from graph import get_main_graph, SubgraphConfig
from knowledge_base import KnowledgeBase
from model_factory import ModelParameters
from skills import seed_skills
from tools.zap_tools import ZapClient, make_zap_tools, setup_zap_context
from tools.kb_tools import make_kb_tools


def _resolve_prompts(prompts: dict[str, str], base_dir: Path, where: str) -> dict[str, str]:
    """Replace each prompt path with the contents of the referenced markdown file.

    `where` is a human-readable label (e.g. "[planner.prompts]") used in error messages.
    Relative paths are resolved against ``base_dir``; absolute paths are used as-is.
    """
    resolved: dict[str, str] = {}
    for key, value in prompts.items():
        raw = Path(value)
        path = raw if raw.is_absolute() else (base_dir / raw)
        try:
            resolved[key] = path.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Prompt file for {where}.{key} not found: '{value}' "
                f"(resolved to {path.resolve()})"
            ) from e
    return resolved


def read_config(config_path: str | None = None) -> dict:
    """Read the TOML configuration and inline external prompts.

    Each ``[*.prompts]`` block's values are treated as paths to markdown files
    (relative to the config file's directory, or absolute). The file contents
    replace the path values before the config is returned, so downstream code
    consumes inline prompt strings transparently.

    Args:
        config_path: Path to the TOML config file.  Falls back to the
            ``SAGA_CONFIG`` env var, then ``saga.toml``.
    """
    import os
    config_path = config_path or os.environ.get("SAGA_CONFIG", "saga.toml")
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    base_dir = Path(config_path).resolve().parent
    if "prompts" in config.get("summarizer", {}):
        config["summarizer"]["prompts"] = _resolve_prompts(
            config["summarizer"]["prompts"], base_dir, "[summarizer.prompts]"
        )
    if "prompts" in config.get("planner", {}):
        config["planner"]["prompts"] = _resolve_prompts(
            config["planner"]["prompts"], base_dir, "[planner.prompts]"
        )
    for agent_key, agent_cfg in config.get("agents", {}).items():
        if "prompts" in agent_cfg:
            agent_cfg["prompts"] = _resolve_prompts(
                agent_cfg["prompts"], base_dir, f"[agents.{agent_key}.prompts]"
            )
    for target_key, target_cfg in config.get("targets", {}).items():
        if "human_prompt" in target_cfg:
            target_cfg["human_prompt"] = _resolve_prompts(
                {"human_prompt": target_cfg["human_prompt"]},
                base_dir,
                f"[targets.{target_key}]",
            )["human_prompt"]
    return config


def dict_to_tuple_list(d: dict) -> list[tuple]:
    """Convert a dictionary to a list of key-value tuples."""
    return [(k, v) for k, v in d.items()]


def _format_agent_description(base: str, tools: list[BaseTool]) -> str:
    """Append a formatted tool list to an agent description for the planner LLM."""
    lines = [base.strip(), "", "Available tools:"]
    for t in tools:
        summary = next((ln.strip() for ln in t.description.splitlines() if ln.strip()), t.name)
        lines.append(f"  - {t.name}: {summary}")
    return "\n".join(lines)


def build_graph(config: dict, zap: ZapClient | None = None, *, run_id: str | None = None):
    """Construct the main LangGraph from configuration.

    Args:
        config: Parsed ``saga.toml`` contents.
        zap: The run's ``ZapClient`` — typically pointed at a container
            spawned by ``tools/zap_launcher.py`` for this run.  Pass
            ``None`` for structure-only use (e.g. rendering the graph
            diagram): tool closures are built against a placeholder
            client that is never invoked, and no live ZAP context setup
            is performed.
        run_id: Optional run identifier used to derive a unique default
            ZAP context name (``sagapt_{run_id}``) when the config does
            not specify one, avoiding cross-run context-name collisions
            if a ZAP instance is ever reused.

    Returns:
        A 4-tuple of ``(compiled_graph, planner_cfg, target_url, knowledge_base)``.
    """
    logger = logging.getLogger(__name__)

    target = config["general"]["target"]
    logger.info("Target URL: %s", target)

    structure_only = zap is None
    if structure_only:
        # Placeholder client — its ZAPv2 constructor does no I/O; the closures
        # produced by make_zap_tools capture it but callers of build_graph in
        # structure-only mode (Mermaid rendering) never invoke those tools.
        zap = ZapClient(url="http://placeholder.invalid")

    def _model_params(section: dict) -> ModelParameters:
        """Construct ModelParameters from a config section."""
        return ModelParameters(
            provider=section["model_provider"],
            model_name=section["model_name"],
            temperature=section["temperature"],
            model_kwargs=section.get("model_kwargs", {}),
        )

    planner_cfg = config["planner"]
    planner_params = _model_params(planner_cfg)
    logger.debug(
        "Planner model: %s/%s (temperature=%s, model_kwargs=%s)",
        planner_params["provider"],
        planner_params["model_name"],
        planner_params["temperature"],
        planner_params["model_kwargs"],
    )

    # --- Knowledge base ---
    kb = KnowledgeBase()
    # Seed the domain-knowledge skills library into the KB under "skills/" so the
    # DAST/exploitation agents can read it via kb_get. Seeded before any subgraph
    # runs, so "skills" also shows up in the agents' {kb_keys} prompt listing.
    seeded = seed_skills(kb)
    logger.info("Knowledge base initialised; seeded %d skill(s).", seeded)

    # --- ZAP context setup ---
    # `include` falls back to a pattern derived from the run's own (always
    # required) target when the caller supplies no explicit [zap] config —
    # e.g. API/frontend-triggered runs, which today omit `zap` entirely. This
    # is computed unconditionally (independent of whether a live ZAP context
    # is set up below) so the tools/url_scope.py allowlist in make_zap_tools
    # is always active, even for a run with no [zap] block or no live ZAP
    # context — see tools/url_scope.py for how include/exclude are enforced.
    zap_cfg = config.get("zap") or {}
    include = zap_cfg.get("include") or [rf"\Q{target}\E.*"]
    exclude = zap_cfg.get("exclude", [])
    # Prefer a per-run default context name so a reused ZAP instance never
    # collides on the old shared "sagapt" name (harmless with the per-run
    # launcher, but a footgun during development).
    default_context = f"sagapt_{run_id}" if run_id else "sagapt"
    context_name = zap_cfg.get("context_name", default_context)
    # setup_zap_context talks to a live ZAP instance, so it stays conditional
    # on an explicit [zap] block (e.g. the fake-model test suite has none and
    # must not require live infrastructure) AND on having a real ZAP client —
    # structure-only callers (Mermaid rendering) skip it too. The URL
    # allowlist above does not depend on this.
    context_id: int | None = None
    if zap_cfg and not structure_only:
        context_id = setup_zap_context(
            zap,
            context_name,
            include,
            exclude,
        )

    # --- Shared HTTP session (cookie persistence across all tool calls in this run) ---
    http_session = requests.Session()
    zap_tool_map = make_zap_tools(
        zap,
        http_session,
        context_id,
        context_name=context_name if zap_cfg else None,
        spider_exclude=zap_cfg.get("spider_exclude", []) if zap_cfg else None,
        include=include,
        exclude=exclude,
    )
    logger.debug("ZAP tool map created with %d tool(s).", len(zap_tool_map))

    # --- Summariser ---
    # Per-agent ModelParameters are built below in the agent loop; the prompt
    # template is shared across all agents.
    summarizer_cfg = config["summarizer"]
    summarizer_prompt = ChatPromptTemplate(dict_to_tuple_list(summarizer_cfg["prompts"]))
    logger.info(
        "Summariser model: %s/%s.",
        summarizer_cfg["model_provider"],
        summarizer_cfg["model_name"],
    )

    # --- Agents ---
    subgraphs: list[SubgraphConfig] = []
    agents_cfg = config["agents"]
    logger.info("Found %d agent(s) in config.", len(agents_cfg))

    for subgraph_name, params in agents_cfg.items():
        logger.info(
            "Configuring agent '%s' with model '%s/%s'.",
            subgraph_name,
            params["model_provider"],
            params["model_name"],
        )
        logger.debug(
            "Agent '%s' settings — temperature=%s, model_kwargs=%s",
            subgraph_name,
            params["temperature"],
            params.get("model_kwargs", {}),
        )
        tool_configs: list[dict] = [
            {"name": t, "summarize": False} if isinstance(t, str) else t
            for t in params["tools"]
        ]
        for tc in tool_configs:
            if tc["name"] not in zap_tool_map:
                raise ValueError(
                    f"Agent '{subgraph_name}' references unknown tool '{tc['name']}'. "
                    f"Valid tools: {sorted(zap_tool_map.keys())}"
                )
        agent_tools = [zap_tool_map[tc["name"]] for tc in tool_configs]
        no_summarize_tools = frozenset(
            tc["name"] for tc in tool_configs if not tc.get("summarize", False)
        )
        kb_tool_list = make_kb_tools(kb, subgraph_name)
        agent_model_params = _model_params(params)
        summarizer_params = _model_params(summarizer_cfg)
        subgraphs.append(SubgraphConfig(
            name=subgraph_name,
            description=_format_agent_description(params["description"], agent_tools),
            model_params=agent_model_params,
            prompts=ChatPromptTemplate(dict_to_tuple_list(params["prompts"])),
            tools=agent_tools,
            kb_tools=kb_tool_list,
            kb=kb,
            summarizer_model_params=summarizer_params,
            summarizer_prompt=summarizer_prompt,
            zap_tool_names=frozenset(t.name for t in agent_tools),
            no_summarize_tools=no_summarize_tools,
            reflection_interval=params.get("reflection_interval", 8),
            max_tool_calls=params.get("max_tool_calls", 28),
            http_session=http_session,
        ))

    logger.debug("Building main graph with %d subgraph(s).", len(subgraphs))
    main_graph = get_main_graph(
        planner_model_params=planner_params,
        subgraphs=subgraphs,
        kb=kb,
    )
    logger.info("Main graph compiled successfully.")
    return main_graph, planner_cfg, target, kb
