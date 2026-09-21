import json
import logging
from typing import TypedDict
from langgraph.graph.state import BaseModel, CompiledStateGraph
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from pydantic import Field
from langchain_core.runnables import RunnableConfig
import requests

from knowledge_base import KnowledgeBase
from model_factory import ModelParameters, get_tool_model
from graph.llm_retry import ainvoke_with_retry
from graph.message_content import extract_text, has_usable_output
from graph.state import create_subgraph_state, MainState
from graph import get_subgraph
from tools.kb_tools import make_planner_kb_tools

logger = logging.getLogger(__name__)

class SubgraphConfig(TypedDict):
    """Configuration for passing a subgraph into the main graph factory."""
    name: str
    description: str
    model_params: ModelParameters
    prompts: ChatPromptTemplate
    tools: list                                  # ZAP tools only
    kb_tools: list                               # KB tools from make_kb_tools(kb)
    kb: object                                   # Shared KnowledgeBase instance
    summarizer_model_params: ModelParameters
    summarizer_prompt: ChatPromptTemplate
    zap_tool_names: frozenset                    # frozenset(t.name for t in tools)
    no_summarize_tools: frozenset                # tool names that bypass LLM summarization
    reflection_interval: int                     # force a tool-less reflection turn this often
    max_tool_calls: int                          # hard cap on tool-call turns per invocation
    http_session: requests.Session               # shared session; cookies cleared per dispatch

class SubgraphToolSchema(BaseModel):
    """The schema the LLM must follow when invoking a subgraph."""
    instructions: str = Field(..., description="Specific, detailed instructions for this agent to execute.")
    execution_name: str = Field(
        ...,
        description=(
            "A short label for this specific invocation, e.g. 'DAST on search endpoint' or "
            "'Initial recon'. Distinct dispatches of the same agent must use distinct names — "
            "this organizes the run's knowledge-base output per invocation."
        ),
    )

def get_main_graph(
        planner_model_params: ModelParameters,
        subgraphs: list[SubgraphConfig],
        kb: KnowledgeBase,
    ) -> CompiledStateGraph:
    """
    Build and compile the main (planner) LangGraph.

    The planner LLM dispatches work to sub-agents by issuing tool calls whose
    names match a registered subgraph. Each subgraph runs its own ReAct loop
    and returns a ToolMessage that feeds back into the planner. The planner
    also gets read-only knowledge-base tools (``kb_get``, ``kb_list_dir``) so
    it can look up agent findings directly instead of relying solely on
    agents relaying results back to it.
    """
    logger.info(
        "Building main graph with planner '%s/%s' and %d subgraph(s).",
        planner_model_params["provider"],
        planner_model_params["model_name"],
        len(subgraphs),
    )

    tools = []
    for config in subgraphs:
        logger.debug("Registering subgraph '%s' as a planner tool.", config["name"])
        tool = StructuredTool.from_function(
            func=lambda instructions, execution_name: None,  # Never actually called; only defines the schema for the LLM
            name=config["name"],
            description=config["description"],
            args_schema=SubgraphToolSchema
        )
        tools.append(tool)

    planner_kb_tools = make_planner_kb_tools(kb)
    planner_kb_tool_names = frozenset(t.name for t in planner_kb_tools)
    kb_tool_node = ToolNode(planner_kb_tools)

    logger.debug(
        "Binding %d agent-dispatch tool(s) and %d KB tool(s) to planner model.",
        len(tools),
        len(planner_kb_tools),
    )
    llm = get_tool_model(planner_model_params, tools=tools + planner_kb_tools)

    _EMPTY_RESPONSE_RETRIES = 2  # extra nudges if the planner LLM returns nothing at all

    # <-- CHANGED: Made async and added RunnableConfig
    async def planner_node(state: MainState, config: RunnableConfig) -> dict:
        """Invoke the planner LLM with the current message history.

        A turn with no usable text and no tool calls would otherwise silently
        end the run via ``route_planner`` — a real model failure mode, not a
        deliberate stop (notably a Gemini-3 turn that spends its whole output
        budget on reasoning and returns a textless content block). When that
        happens, a corrective ``HumanMessage`` is injected telling the planner
        it must either dispatch an agent or write the final report, and the
        LLM is re-invoked. Capped at ``_EMPTY_RESPONSE_RETRIES`` nudges so a
        model that keeps returning nothing can't loop forever.
        """
        history = state.get("messages", [])
        new_messages: list[BaseMessage] = []
        logger.info("Planner node: invoking LLM with %d message(s).", len(history))

        for _empty_attempt in range(_EMPTY_RESPONSE_RETRIES + 1):
            response = await ainvoke_with_retry(
                llm, history + new_messages, config, label="Planner"
            )
            tool_calls = getattr(response, "tool_calls", None)
            # ``has_usable_output`` — not ``response.content`` — because a
            # Gemini-3 turn that burns its whole output budget on reasoning
            # returns a truthy-but-textless content list that would otherwise
            # sail past this guard (see graph.message_content).
            if has_usable_output(response):
                break
            logger.error("Planner LLM returned an empty message (no usable text, no tool calls).")
            if _empty_attempt == _EMPTY_RESPONSE_RETRIES:
                logger.warning(
                    "Planner: still empty after %d nudge(s); ending turn as-is.",
                    _EMPTY_RESPONSE_RETRIES,
                )
                break
            new_messages.append(response)
            new_messages.append(
                HumanMessage(
                    content="Your last response had no content and no tool calls. Either call "
                    "an agent tool to continue the engagement, or, if you are done, write your "
                    "final penetration testing report now. Do not stop with nothing."
                )
            )

        if tool_calls:
            logger.info(
                "Planner issued %d tool call(s): [%s].",
                len(tool_calls),
                ", ".join(tc["name"] for tc in tool_calls),
            )
            for tc in tool_calls:
                logger.debug("Planner tool call: %s(%s)", tc["name"], json.dumps(tc["args"]))
        else:
            logger.info("Planner produced a final response (no tool calls).")
            logger.debug("Planner final response content: %s", extract_text(response.content)[:200] or "<empty>")

        new_messages.append(response)
        return {"messages": new_messages}


    def make_subgraph_node(config_dict: SubgraphConfig):
        """Closure that creates a node function for the given subgraph config."""
        # Note: I renamed the outer parameter to config_dict just to avoid shadowing 
        # the internal 'config' argument, making it cleaner.
        graph = get_subgraph(
            name=config_dict["name"],
            model_params=config_dict["model_params"],
            tools=config_dict["tools"],
            kb_tools=config_dict["kb_tools"],
            summarizer_model_params=config_dict["summarizer_model_params"],
            summarizer_prompt=config_dict["summarizer_prompt"],
            kb=config_dict["kb"],
            zap_tool_names=config_dict["zap_tool_names"],
            no_summarize_tools=config_dict["no_summarize_tools"],
            reflection_interval=config_dict["reflection_interval"],
            max_tool_calls=config_dict["max_tool_calls"],
        )

        # 1. CHANGED: Rename 'runnable_config' to exactly 'config'
        async def subgraph_node(state: MainState, config: RunnableConfig) -> dict:
            """
            Execute the subgraph for this agent.
            """
            # Clear leftover session cookies so this dispatch starts
            # unauthenticated. Without this, cookies from a prior dispatch
            # leak in: if the previous agent logged in and didn't log out,
            # the target may skip form processing (e.g. login pages that
            # redirect already-authenticated users to the homepage), hiding
            # vulnerabilities from the current agent's probes.
            config_dict["http_session"].cookies.clear()
            last_message = state["messages"][-1]
            tool_call = next(tc for tc in last_message.tool_calls if tc["name"] == config_dict["name"])
            instructions = tool_call["args"]["instructions"]
            execution_name = tool_call["args"]["execution_name"]

            logger.info("Executing subgraph '%s' ('%s').", config_dict["name"], execution_name)

            fmt_args: dict = {"target": state["target"], "task": instructions}
            if "kb_keys" in config_dict["prompts"].input_variables:
                dirs = config_dict["kb"].list_dir("")
                fmt_args["kb_keys"] = json.dumps(dirs) if dirs else "None"

            subgraph_state = create_subgraph_state(
                state,
                name=config_dict["name"],
                messages=config_dict["prompts"].format_messages(**fmt_args),
                execution_name=execution_name,
            )

            subgraph_result = await graph.ainvoke(subgraph_state, config=config)

            final_message = (
                subgraph_result["messages"][-1].content
                if subgraph_result and subgraph_result.get("messages")
                else "Task completed with no output."
            )

            return {"messages": [ToolMessage(
                content=final_message,
                tool_call_id=tool_call["id"],
                name=config_dict["name"],
            )]}

        return subgraph_node


    _MULTI_CALL_REJECT = "_multi_call_reject"
    _KB_TOOLS = "kb_tools"

    async def multi_call_reject_node(state: MainState, config: RunnableConfig) -> dict:
        """Return error ToolMessages for every tool call when the planner issued more than one."""
        last_message = state["messages"][-1]
        logger.warning(
            "Planner issued %d tool calls in one turn; rejecting all. "
            "Only one agent may be invoked per turn, and KB reads may not be mixed with a dispatch.",
            len(last_message.tool_calls),
        )
        return {
            "messages": [
                ToolMessage(
                    content=(
                        "Error: only one agent may be invoked per turn, and knowledge-base reads "
                        "(kb_get/kb_list_dir) may not be mixed with an agent dispatch in the same "
                        "turn. All calls in this turn were rejected. Invoke a single agent, or "
                        "issue KB reads on their own, and wait for the response."
                    ),
                    tool_call_id=tc["id"],
                    name=tc["name"],
                )
                for tc in last_message.tool_calls
            ]
        }

    def route_planner(state: MainState) -> str:
        """Route to the appropriate subgraph node, the KB tool node, or end the workflow."""
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", None)
        if not tool_calls:
            logger.debug("Planner routing → END.")
            return "__end__"
        names = {tc["name"] for tc in tool_calls}
        if names <= planner_kb_tool_names:
            logger.debug("Planner routing → '%s' (%d KB read(s)).", _KB_TOOLS, len(tool_calls))
            return _KB_TOOLS
        if len(tool_calls) > 1:
            logger.debug("Planner issued multiple tool calls → routing to rejection node.")
            return _MULTI_CALL_REJECT
        destination = tool_calls[0]["name"]
        logger.debug("Planner routing → '%s'.", destination)
        return destination


    workflow = StateGraph(MainState)
    workflow.add_node("planner", planner_node)
    workflow.add_node(_MULTI_CALL_REJECT, multi_call_reject_node)
    workflow.add_edge(_MULTI_CALL_REJECT, "planner")
    workflow.add_node(_KB_TOOLS, kb_tool_node)
    workflow.add_edge(_KB_TOOLS, "planner")

    for config in subgraphs:
        workflow.add_node(config["name"], make_subgraph_node(config))
        workflow.add_edge(config["name"], "planner")
        logger.debug("Graph edge added: '%s' → 'planner'.", config["name"])

    path_map = {config["name"]: config["name"] for config in subgraphs}
    path_map[_MULTI_CALL_REJECT] = _MULTI_CALL_REJECT
    path_map[_KB_TOOLS] = _KB_TOOLS
    path_map["__end__"] = END

    workflow.add_edge(START, "planner")
    workflow.add_conditional_edges("planner", route_planner, path_map)

    compiled = workflow.compile()
    logger.info("Main graph compiled successfully.")
    return compiled