import operator
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage


class SharedState(TypedDict):
    """Shared state for all agents in the system."""

    target: str
    """The target of the engagement, e.g., 'https://example.com'."""


class _PendingToolResult(TypedDict):
    """Raw ZAP tool result dict buffered by ``zap_execute`` for ``summarize``."""

    tool_call_id: str
    tool_name: str
    tool_args: dict
    raw_output: dict
    kb_keys_modified: list[str]
    """KB keys written directly by the tool itself (before summarisation)."""
    kb_key: str | None
    """Agent-provided KB key extracted from the tool's JSON output; overrides
    the auto-generated key in ``summarize_node`` when present."""


class SubgraphState(SharedState):
    """State for a specific subgraph/agent."""

    name: str
    """The name of the agent, e.g., 'recon'."""
    execution_name: str
    """Planner-provided label for this specific invocation, e.g. 'Initial recon'.
    Used to scope this invocation's tool_logs in the knowledge base."""
    messages: Annotated[list[BaseMessage], operator.add]
    """Accumulated conversation history (system, human, AI, tool messages)."""
    pending_tool_results: list[_PendingToolResult]
    """Raw ZAP tool outputs waiting to be summarised; set by ``zap_execute``,
    consumed and cleared by ``summarize``."""
    tool_call_count: int
    """Count of agent turns that issued >=1 tool call this invocation (one
    multi-tool-call turn still counts as 1). Drives the reflection/hard-cap router."""


class MainState(SharedState):
    """State for the main graph (planner)."""

    messages: Annotated[list[BaseMessage], operator.add]


def create_subgraph_state(
    main_state: MainState, name: str, messages: list[BaseMessage], execution_name: str
) -> SubgraphState:
    """Create a clean subgraph state, copying shared target and seeding messages."""
    return SubgraphState(
        target=main_state["target"],
        name=name,
        execution_name=execution_name,
        messages=messages,
        pending_tool_results=[],
        tool_call_count=0,
    )
