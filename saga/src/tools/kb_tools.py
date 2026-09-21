"""Knowledge base tools for SagaPT agents and the planner.

Agent-facing tools are created via the ``make_kb_tools`` factory, which binds
them to the shared ``KnowledgeBase`` instance. They are injected into every
agent automatically — they do not need to be listed in ``saga.toml``.

The planner gets a read-only subset via ``make_planner_kb_tools`` — it may
look up prior findings and tool logs across the whole engagement, but cannot
write to the knowledge base (that stays an agent-only capability via
``register_finding``).
"""

import json
import logging

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from knowledge_base import KnowledgeBase, slugify


logger = logging.getLogger(__name__)

# Canonical names for KB tools — used by subgraph routing to distinguish them
# from ZAP tools.
KB_TOOL_NAMES: frozenset[str] = frozenset({"kb_list_dir", "kb_get", "register_finding"})

# Canonical names for the planner's read-only KB tools — used by main graph
# routing to distinguish them from agent-dispatch tool calls.
PLANNER_KB_TOOL_NAMES: frozenset[str] = frozenset({"kb_list_dir", "kb_get"})

# Maximum characters returned by ``kb_get`` in a single call. The knowledge base
# stores full untruncated tool outputs (e.g. an SPA JS bundle can be >1 MB), so an
# unbounded read would flood the agent's context window in one shot — exactly what
# the http_get/http_post in-message body cap in ``subgraph.py`` exists to prevent.
# A read above this limit is truncated to it and prefixed with a notice so the
# agent knows the entry is only partially shown and stays retrievable in pieces.
_KB_GET_CHAR_LIMIT = 20_000


class _KBGetArgs(BaseModel):
    key: str = Field(..., description="File path to read from the knowledge base.")


class _KBListDirArgs(BaseModel):
    path: str = Field(
        default="",
        description='Directory path to list. Use "" or "." for the root.',
    )


class _RegisterFindingArgs(BaseModel):
    title: str = Field(..., description="Short descriptive title for the finding (e.g. 'sql_injection_login').")
    content: str = Field(..., description="Full finding description in markdown.")


def _make_kb_get_tool(kb: KnowledgeBase) -> BaseTool:
    """Build the read-only ``kb_get`` tool bound to *kb*."""

    def kb_get(key: str) -> str:
        """
        Read a file from the knowledge base by its path.

        Use ``kb_list_dir`` to navigate the directory structure, then call this
        with the exact file path (e.g. ``"recon/initial_recon/tool_logs/get_login.md"``).
        Returns the file contents, or an error message if the path does not exist.

        Entries larger than the read limit (currently 20,000 characters) are
        truncated to it and prefixed with a notice; the full content stays stored
        in the knowledge base. If you need more than the shown portion, work with
        it in pieces rather than expecting the whole file in one call.
        """
        logger.info("KB get: '%s'.", key)
        value = kb.get(key)
        if value is None:
            logger.debug("KB get: path '%s' not found.", key)
            return f"Not found: {key!r}"
        if len(value) > _KB_GET_CHAR_LIMIT:
            logger.debug(
                "KB get: '%s' is %d chars, truncating to %d for the tool result.",
                key, len(value), _KB_GET_CHAR_LIMIT,
            )
            notice = (
                f"[Knowledge base entry {key!r} is {len(value)} characters — too "
                f"large to return in full. Showing the first {_KB_GET_CHAR_LIMIT} "
                f"characters below; the full entry remains stored in the knowledge "
                f"base. Do not try to read it whole — work with it in smaller "
                f"pieces or rely on the summary/alerts instead.]\n\n"
            )
            return notice + value[:_KB_GET_CHAR_LIMIT]
        logger.debug("KB get: found '%s' (%d chars).", key, len(value))
        return value

    return StructuredTool.from_function(
        func=kb_get,
        name="kb_get",
        description=kb_get.__doc__ or "Read a file from the knowledge base.",
        args_schema=_KBGetArgs,
    )


def _make_kb_list_dir_tool(kb: KnowledgeBase) -> BaseTool:
    """Build the read-only ``kb_list_dir`` tool bound to *kb*."""

    def kb_list_dir(path: str = "") -> str:
        """
        List entries directly under a knowledge base directory.

        Returns a JSON array of file names and subdirectory names at the given
        path. Use ``""`` or ``"."`` to list the root. Drill down to explore:

          kb_list_dir("")                              → ["recon", "dast"]
          kb_list_dir("recon")                         → ["findings", "initial_recon"]
          kb_list_dir("recon/initial_recon/tool_logs")  → ["get_login.md", "get_login_raw.json", ...]

        Read a file with ``kb_get("recon/initial_recon/tool_logs/get_login.md")``.
        """
        entries = kb.list_dir(path)
        logger.debug("KB list_dir('%s'): %d entries.", path, len(entries))
        return json.dumps(entries)

    return StructuredTool.from_function(
        func=kb_list_dir,
        name="kb_list_dir",
        description=kb_list_dir.__doc__ or "List a knowledge base directory.",
        args_schema=_KBListDirArgs,
    )


def make_planner_kb_tools(kb: KnowledgeBase) -> list[BaseTool]:
    """Return read-only KB tools (``kb_get``, ``kb_list_dir``) bound to *kb*.

    Used by the planner to look up agent findings and tool logs directly
    instead of relying solely on agents relaying results back to it. Unlike
    ``make_kb_tools``, this omits ``register_finding`` — the planner does not
    write to the knowledge base.
    """
    return [_make_kb_get_tool(kb), _make_kb_list_dir_tool(kb)]


def make_kb_tools(kb: KnowledgeBase, agent_name: str) -> list[BaseTool]:
    """Return KB tools bound to *kb* and scoped to *agent_name*."""

    def register_finding(title: str, content: str) -> str:
        """
        Store a security finding in the knowledge base.

        Writes *content* (markdown) to ``{agent}/findings/{slug}.md`` where
        *slug* is derived from *title*. Use this to record confirmed
        vulnerabilities, interesting endpoints, credentials, or any other
        noteworthy discovery before finishing your turn.

        Fails if a finding with the same title already exists — read it
        first with ``kb_get`` to check whether it already covers what you
        found before picking a new, more specific title.

        Returns the path the finding was stored at.
        """
        slug = slugify(title)
        if not slug:
            return "Error: title produced an empty slug — use alphanumeric characters."
        path = f"{agent_name}/findings/{slug}.md"
        if kb.get(path) is not None:
            logger.info("KB register_finding: '%s' rejected — '%s' already exists.", title, path)
            return (
                f"Error: a finding named {slug!r} already exists at {path!r}. "
                "Read it first (kb_get) if you want to confirm or extend it — "
                "pick a different, more specific title if this is a genuinely new finding."
            )
        kb.store(path, content)
        logger.info("KB register_finding: '%s' → '%s'.", title, path)
        return f"Finding stored at: {path!r}"

    return [
        _make_kb_get_tool(kb),
        _make_kb_list_dir_tool(kb),
        StructuredTool.from_function(
            func=register_finding,
            name="register_finding",
            description=register_finding.__doc__ or "Store a security finding.",
            args_schema=_RegisterFindingArgs,
        ),
    ]
