"""Agent subgraph factory for SagaPT.

Each agent runs as an independent ReAct loop compiled from this factory.
The flow is:

    START → agent → should_continue:
      → "zap_execute"  ZAP tool execution → "summarize"  LLM summarisation + KB store → route_after_tools
      → "kb_tools"   KB query/list execution → route_after_tools
      → "__end__"    END

route_after_tools sends the loop back to "agent" normally, but every
``reflection_interval`` tool-call turns (and at the hard cap
``max_tool_calls``) it instead routes to "reflect": a tool-less checkpoint
turn that forces the agent to justify its approach before continuing, or to
wrap up with a final summary once the hard cap is reached.

ZAP tool results are never written to the message history in raw form - they
are summarised by a second LLM call before being returned as ``ToolMessage``s,
keeping the agent's context window compact. Summaries are simultaneously
stored in the shared ``KnowledgeBase`` for cross-agent retrieval.

Agents are instructed in their system prompt not to issue both ZAP and KB tool
calls in a single turn; the routing logic treats any ZAP tool call as taking
the ZAP path.
"""

import json
import logging
from typing import Literal

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from graph.llm_retry import ainvoke_with_retry
from graph.message_content import has_usable_output
from graph.state import SubgraphState
from knowledge_base import KnowledgeBase, slugify
from model_factory import ModelParameters, get_model, get_tool_model
from tools.kb_tools import KB_TOOL_NAMES

logger = logging.getLogger(__name__)


class Truncate:
    """Utility class to truncate long strings for logging purposes."""

    def __init__(self, data: object, max_len: int = 20) -> None:
        self.data = str(data)
        self.max_len = max_len

    def __str__(self) -> str:
        if len(self.data) <= self.max_len:
            return self.data
        snippet = self.data[: self.max_len - 3]
        newline_pos = snippet.find("\n")
        if newline_pos != -1:
            snippet = snippet[:newline_pos]
        return snippet + "..."


# Maximum characters of the serialized tool output JSON passed to the summariser LLM.
_SUMMARISER_INPUT_LIMIT = 20_000

# Maximum characters of a response ``body`` field echoed back to the agent in a
# tool-result message. The full untruncated body is always persisted to the
# knowledge base (see ``summarize_node``); only this in-message view is capped, so a
# large payload (e.g. an SPA JS bundle) never floods the context window while staying
# retrievable via kb_get. Applied in the ``no_summarize`` path — the one every tool
# currently takes — so it must not depend on the summariser LLM running.
_MESSAGE_BODY_LIMIT = 10_000


def _truncate_for_summariser(raw: dict, budget: int = _SUMMARISER_INPUT_LIMIT) -> str:
    """Serialize *raw* to a JSON string within *budget* characters.

    ``alerts`` is always preserved verbatim (security-critical). ``body``
    (str field, from http_get/http_post) is shrunk first, then
    ``discovered_urls`` (list field, from spider), using binary search to
    find the exact cut point. If even after both fields are emptied the result
    still exceeds *budget*, the best-effort serialization is returned as-is.
    """
    candidate = json.dumps(raw)
    if len(candidate) <= budget:
        return candidate

    d = dict(raw)

    original_len = len(candidate)

    if "body" in d and isinstance(d["body"], str):
        original_body = d["body"]
        lo, hi = 0, len(original_body)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            d["body"] = original_body[:mid]
            if len(json.dumps(d)) <= budget:
                lo = mid
            else:
                hi = mid - 1
        d["body"] = original_body[:lo]
        result = json.dumps(d)
        if len(result) <= budget:
            logger.warning(
                "Summariser input truncated: 'body' shortened from %d to %d chars (budget=%d, original=%d).",
                len(original_body), lo, budget, original_len,
            )
            return result

    if "discovered_urls" in d and isinstance(d["discovered_urls"], list):
        original_urls = list(d["discovered_urls"])
        lo, hi = 0, len(original_urls)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            d["discovered_urls"] = original_urls[:mid]
            if len(json.dumps(d)) <= budget:
                lo = mid
            else:
                hi = mid - 1
        d["discovered_urls"] = original_urls[:lo]
        logger.warning(
            "Summariser input truncated: 'discovered_urls' shortened from %d to %d entries (budget=%d, original=%d).",
            len(original_urls), lo, budget, original_len,
        )

    return json.dumps(d)


def _truncate_body_for_message(
    raw: dict, limit: int = _MESSAGE_BODY_LIMIT
) -> tuple[dict, bool]:
    """Return a view of *raw* with its ``body`` field capped for the LLM message.

    Only the ``body`` str field (produced by http_get/http_post) is affected; the
    knowledge base keeps the full untruncated *raw*. This trimmed copy is what the
    agent sees in its ToolMessage, so a large response body (e.g. an SPA JavaScript
    bundle) never floods the context window while the full copy stays retrievable
    via kb_get.

    Returns the (possibly unchanged) dict plus a flag indicating whether the body
    was actually shortened.
    """
    body = raw.get("body")
    if isinstance(body, str) and len(body) > limit:
        trimmed = dict(raw)
        trimmed["body"] = body[:limit]
        return trimmed, True
    return raw, False


def _make_slug(tool_name: str, tool_args: dict, label: str | None = None) -> str:
    """Generate a filesystem-safe slug for a KB entry.

    Uses *label* (the agent-provided ``kb_key`` argument) when available;
    otherwise derives the slug from *tool_name* and the first string argument.
    The result is lowercase alphanumerics and underscores, max 80 chars.
    """
    if label:
        raw = label
    else:
        first_str = next(
            (str(v) for v in tool_args.values() if isinstance(v, str)),
            json.dumps(tool_args, separators=(",", ":")),
        )
        raw = f"{tool_name}_{first_str}"
    return slugify(raw)


def get_subgraph(
    name: str,
    model_params: ModelParameters,
    tools: list[BaseTool],
    kb_tools: list[BaseTool],
    summarizer_model_params: ModelParameters,
    summarizer_prompt: ChatPromptTemplate,
    kb: KnowledgeBase,
    zap_tool_names: frozenset[str],
    no_summarize_tools: frozenset[str] = frozenset(),
    reflection_interval: int = 8,
    max_tool_calls: int = 28,
) -> CompiledStateGraph:
    """Build and compile a ReAct subgraph for the given agent.

    Args:
        name: Agent name, used in log messages.
        model_params: LLM configuration for the agent.
        tools: ZAP tools available to this agent.
        kb_tools: Knowledge-base tools injected for all agents.
        summarizer_model_params: LLM configuration for the summariser.
        summarizer_prompt: Prompt template for the summariser (variables:
            ``tool_name``, ``tool_args``, ``raw_output``).
        kb: Shared ``KnowledgeBase`` instance.
        zap_tool_names: Set of ZAP tool names for routing decisions.
        no_summarize_tools: Tool names whose raw output is returned directly to
            the agent without an LLM summarisation pass.
        reflection_interval: Force a tool-less reflection turn every this many
            agent tool-call turns, so the agent must justify its approach
            before continuing.
        max_tool_calls: Hard cap on agent tool-call turns; the subgraph ends
            after one final, tool-less reflection turn once reached.
    """
    logger.info(
        "Building subgraph '%s' with model '%s/%s', %d ZAP tool(s), %d KB tool(s).",
        name,
        model_params["provider"],
        model_params["model_name"],
        len(tools),
        len(kb_tools),
    )
    logger.debug(
        "Subgraph '%s' ZAP tools: [%s].",
        name,
        ", ".join(t.name for t in tools),
    )

    llm = get_tool_model(model_params, tools=tools + kb_tools)
    summarizer_llm = get_model(summarizer_model_params)

    # Map tool name → tool object for fast lookup inside the custom ZAP node.
    tool_map: dict[str, BaseTool] = {t.name: t for t in tools}
    # KB tool map for handling mixed ZAP+KB turns (agent shouldn't mix, but may).
    kb_tool_map: dict[str, BaseTool] = {t.name: t for t in kb_tools}

    async def _summarize(
        tool_name: str,
        tool_args: dict,
        raw_output: dict,
        config: RunnableConfig,
    ) -> str:
        """Call the summariser LLM and return the summary string."""
        serialized = _truncate_for_summariser(raw_output)
        messages = summarizer_prompt.format_messages(
            tool_name=tool_name,
            tool_args=json.dumps(tool_args),
            raw_output=serialized,
        )
        logger.debug(
            "Summariser: running for tool '%s' (%d chars).", tool_name, len(serialized)
        )
        result = await ainvoke_with_retry(
            summarizer_llm, messages, config, label=f"Summarizer ({tool_name})"
        )
        summary = (
            result.content if isinstance(result.content, str) else str(result.content)
        )
        logger.debug("Summariser: summary=%d chars.", len(summary))
        return summary

    _EMPTY_RESPONSE_RETRIES = 2  # extra nudges if the LLM returns nothing at all

    async def _invoke_agent_llm(messages: list[BaseMessage], config: RunnableConfig) -> BaseMessage:
        """Call the agent LLM, retrying transient provider failures.

        See ``graph/llm_retry.py`` for what counts as transient (malformed
        tool-call JSON, Vertex 5xx, and the masked google-genai async
        error-handler crash).
        """
        return await ainvoke_with_retry(llm, messages, config, label=f"Agent '{name}'")

    async def agent_node(state: SubgraphState, config: RunnableConfig) -> dict:
        """Invoke the agent LLM with the current message history.

        A turn with no usable text and no tool calls would otherwise silently
        end the subgraph via ``should_continue`` — a real model failure mode,
        not a deliberate stop (notably a Gemini-3 turn that spends its whole
        output budget on reasoning and returns a textless content block). When
        that happens, a corrective ``HumanMessage`` is injected telling the
        model it must either call a tool or write a final report, and the LLM
        is re-invoked. Capped at ``_EMPTY_RESPONSE_RETRIES`` nudges so a model
        that keeps returning nothing can't loop forever.
        """
        history = state.get("messages", [])
        new_messages: list[BaseMessage] = []
        logger.debug(
            "Agent '%s': invoking LLM with %d message(s).",
            name,
            len(history),
        )
        logger.info("Agent '%s': querying LLM.", name)

        for _empty_attempt in range(_EMPTY_RESPONSE_RETRIES + 1):
            response = await _invoke_agent_llm(history + new_messages, config)
            tool_calls = getattr(response, "tool_calls", None)
            # ``has_usable_output`` — not ``response.content`` — because a
            # Gemini-3 turn that burns its whole output budget on reasoning
            # returns a truthy-but-textless content list that would otherwise
            # sail past this guard (see graph.message_content).
            if has_usable_output(response):
                break
            logger.error(
                "Agent '%s': LLM returned an empty message (no usable text, no tool calls).",
                name,
            )
            if _empty_attempt == _EMPTY_RESPONSE_RETRIES:
                logger.warning(
                    "Agent '%s': still empty after %d nudge(s); ending turn as-is.",
                    name,
                    _EMPTY_RESPONSE_RETRIES,
                )
                break
            new_messages.append(response)
            new_messages.append(
                HumanMessage(
                    content="Your last response had no content and no tool calls. Either call "
                    "a tool to continue the task, or, if you are done, write a final message "
                    "summarizing what you found (and call register_finding if appropriate) so "
                    "the task ends with a clear result. Do not stop with nothing."
                )
            )

        if tool_calls:
            logger.info(
                "Agent '%s': LLM issued %d tool call(s): [%s].",
                name,
                len(tool_calls),
                ", ".join(tc["name"] for tc in tool_calls),
            )
            for tc in tool_calls:
                logger.debug(
                    "Agent '%s' tool call: %s(%s)",
                    name,
                    tc["name"],
                    json.dumps(tc["args"]),
                )
        else:
            logger.info(
                "Agent '%s': LLM response (no tool calls): %s",
                name,
                Truncate(response.content, max_len=120),
            )

        new_messages.append(response)
        new_count = state.get("tool_call_count", 0) + (1 if tool_calls else 0)
        return {"messages": new_messages, "tool_call_count": new_count}

    async def zap_execute_node(state: SubgraphState, config: RunnableConfig) -> dict:
        """Execute ZAP tools and buffer raw outputs into ``pending_tool_results``.

        Summarisation happens in the subsequent ``summarize`` node so that both
        steps are visible as distinct nodes in the graph visualisation.

        If the agent mixed KB tool calls with ZAP tool calls in a single turn
        (against instructions), the KB calls are executed inline here so every
        tool call gets a ToolMessage response.
        """
        last_ai = state["messages"][-1]
        pending = []
        immediate_messages: list[ToolMessage] = []

        for tc in last_ai.tool_calls:
            if tc["name"] in tool_map:
                tool_obj = tool_map[tc["name"]]
                logger.info("ZAP tool '%s': executing.", tc["name"])
                # ZAP tools are synchronous; .invoke() is safe here.
                raw_output: dict = tool_obj.invoke(tc["args"])
                logger.debug(
                    "ZAP tool '%s': %d keys in output.", tc["name"], len(raw_output)
                )
                tool_kb_keys: list[str] = raw_output.get("kb_keys_modified", [])
                tool_kb_key: str | None = raw_output.get("kb_key") or None
                pending.append(
                    {
                        "tool_call_id": tc["id"],
                        "tool_name": tc["name"],
                        "tool_args": tc["args"],
                        "raw_output": raw_output,
                        "kb_keys_modified": tool_kb_keys,
                        "kb_key": tool_kb_key,
                        "summarize": tc["name"] not in no_summarize_tools,
                    }
                )
            else:
                # KB tool (or unknown) mixed into a ZAP turn — execute immediately.
                kb_tool_obj = kb_tool_map.get(tc["name"])
                if kb_tool_obj is not None:
                    logger.warning(
                        "Agent '%s': KB tool '%s' called alongside ZAP tools; executing inline.",
                        name,
                        tc["name"],
                    )
                    result = kb_tool_obj.invoke(tc["args"])
                    immediate_messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tc["id"],
                            name=tc["name"],
                        )
                    )
                else:
                    logger.error(
                        "Agent '%s': unknown tool '%s' in zap_execute_node.",
                        name,
                        tc["name"],
                    )
                    immediate_messages.append(
                        ToolMessage(
                            content=f"Error: unknown tool '{tc['name']}'",
                            tool_call_id=tc["id"],
                            name=tc["name"],
                        )
                    )

        return {"pending_tool_results": pending, "messages": immediate_messages}

    async def summarize_node(state: SubgraphState, config: RunnableConfig) -> dict:
        """Summarise pending tool results, store in KB, return ToolMessages.

        Consumes ``pending_tool_results`` set by ``zap_execute`` and clears it.
        Tools listed in ``no_summarize_tools`` skip the LLM call and return
        their raw JSON directly; all other tools are summarised first.
        """
        result_messages: list[ToolMessage] = []
        execution_slug = slugify(state["execution_name"])

        for item in state["pending_tool_results"]:
            raw: dict = item["raw_output"]
            slug = _make_slug(
                item["tool_name"], item["tool_args"], label=item.get("kb_key")
            )
            base = f"{name}/{execution_slug}/tool_logs/{slug}"
            raw_kb_key = f"{base}_raw.json"

            alerts: list | None = raw.get("alerts")
            alerts_kb_key: str | None = f"{base}_alerts.json" if alerts is not None else None

            kb.store(raw_kb_key, json.dumps(raw))
            logger.info("KB: stored '%s' (raw output).", raw_kb_key)
            if alerts_kb_key is not None:
                kb.store(alerts_kb_key, json.dumps(alerts))
                logger.info("KB: stored '%s' (alerts).", alerts_kb_key)

            if item["tool_name"] in no_summarize_tools:
                presented, body_truncated = _truncate_body_for_message(raw)
                content_lines = [json.dumps(presented, indent=2), ""]
                if body_truncated:
                    content_lines.append(
                        f"[Response body truncated to {_MESSAGE_BODY_LIMIT} chars in this "
                        f'message. The full untruncated body is stored at "{raw_kb_key}" — '
                        f"retrieve it with kb_get if you need more than what is shown above.]"
                    )
                    content_lines.append("")
                content_lines.append("Stored in knowledge base:")
                content_lines.append(f'  "{raw_kb_key}" — raw output (.json)')
                if alerts_kb_key is not None:
                    content_lines.append(f'  "{alerts_kb_key}" — ZAP alerts (.json)')
            else:
                summary_key = f"{base}.md"
                summary = await _summarize(
                    item["tool_name"], item["tool_args"], raw, config
                )
                kb.store(summary_key, summary)
                logger.info("KB: stored '%s' (summary).", summary_key)
                content_lines = [
                    summary,
                    "",
                    "Stored in knowledge base:",
                    f'  "{summary_key}" — summary (.md)',
                    f'  "{raw_kb_key}" — raw output (.json)',
                ]
                if alerts_kb_key is not None:
                    content_lines.append(f'  "{alerts_kb_key}" — ZAP alerts (.json)')

            result_messages.append(
                ToolMessage(
                    content="\n".join(content_lines),
                    tool_call_id=item["tool_call_id"],
                    name=item["tool_name"],
                )
            )

        return {"messages": result_messages, "pending_tool_results": []}

    reflect_llm = get_model(model_params)

    async def reflect_node(state: SubgraphState, config: RunnableConfig) -> dict:
        """Force a tool-less checkpoint turn where the agent must justify its approach.

        Invoked via ``reflect_llm``, which has no tools bound, so the model is
        mechanically unable to issue another tool call until its next normal
        ``agent`` turn. On the final (hard-cap) checkpoint, the subgraph ends
        right after this turn, so the injected prompt asks for a wrap-up
        summary instead of a progress check.

        In the non-final case, a follow-up ``HumanMessage`` is appended after
        the reflection reply so the message history ends on a human turn, not
        back-to-back assistant turns. Without it, ``agent_node``'s next
        invocation would ask the model to generate a fresh assistant turn
        immediately following its own prior one with nothing new to respond
        to — real models tend to treat that as the conversation already being
        finished (emitting no tool calls), which prematurely ends the
        subgraph via ``should_continue`` and returns control to the planner
        instead of resuming the task.
        """
        count = state.get("tool_call_count", 0)
        final = count >= max_tool_calls
        if final:
            prompt = (
                f"You have reached the hard limit of {max_tool_calls} tool calls for this task "
                "and will not be given another turn. In this final message: summarize what you "
                "attempted, state explicitly whether anything was confirmed, and if not, say the "
                "task is INCONCLUSIVE. Do not attempt further requests."
            )
        else:
            prompt = (
                f"Checkpoint: you have used {count} of your {max_tool_calls} tool-call budget for "
                "this task. Before continuing, briefly state: (1) what you are currently trying to "
                "determine, (2) the evidence gathered so far, (3) whether your current approach is "
                "working or should change. Do not call a tool in this message."
            )
        injected = HumanMessage(content=prompt)
        response = await ainvoke_with_retry(
            reflect_llm, state["messages"] + [injected], config, label=f"Agent '{name}' (reflect)"
        )
        logger.info(
            "Agent '%s': reflection checkpoint at %d/%d tool calls (final=%s).",
            name, count, max_tool_calls, final,
        )
        messages: list[BaseMessage] = [injected, response]
        if not final:
            messages.append(
                HumanMessage(
                    content="Continue the task now, using tools as needed based on your reflection above."
                )
            )
        return {"messages": messages}

    def route_after_tools(state: SubgraphState) -> Literal["agent", "reflect"]:
        """Route to a forced reflection turn at the configured interval or hard cap."""
        count = state.get("tool_call_count", 0)
        if count > 0 and (count >= max_tool_calls or count % reflection_interval == 0):
            return "reflect"
        return "agent"

    def reflect_router(state: SubgraphState) -> Literal["agent", "__end__"]:
        """End the subgraph after the final hard-cap reflection; otherwise resume."""
        if state.get("tool_call_count", 0) >= max_tool_calls:
            return "__end__"
        return "agent"

    kb_tool_node = ToolNode(kb_tools)

    def should_continue(
        state: SubgraphState,
    ) -> Literal["zap_execute", "kb_tools", "__end__"]:
        """Three-way router: ZAP execution, KB tools, or END."""
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", None)
        if not tool_calls:
            logger.debug("Agent '%s': routing → END.", name)
            return "__end__"
        called = {tc["name"] for tc in tool_calls}
        if called & zap_tool_names:
            logger.debug("Agent '%s': routing → 'zap_execute'.", name)
            return "zap_execute"
        logger.debug("Agent '%s': routing → 'kb_tools'.", name)
        return "kb_tools"

    workflow = StateGraph(SubgraphState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("zap_execute", zap_execute_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("kb_tools", kb_tool_node)
    workflow.add_node("reflect", reflect_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("zap_execute", "summarize")
    workflow.add_conditional_edges("summarize", route_after_tools)
    workflow.add_conditional_edges("kb_tools", route_after_tools)
    workflow.add_conditional_edges("reflect", reflect_router)

    app = workflow.compile()
    logger.debug("Subgraph '%s' compiled.", name)
    return app
