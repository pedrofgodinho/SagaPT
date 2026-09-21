"""Deterministic fake LLM for testing SagaPT without real model providers.

Usage::

    from fakes.fake_llm import FakeChatModel

    llm = FakeChatModel(responses=[
        # If the last non-system message contains "spider", call the spider tool.
        ("spider", [{"name": "fake_spider", "args": {"url": "http://target"}}]),
        # Catch-all: any other message returns plain text.
        ("", "Task complete."),
    ])
"""

import json
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import Field


type _ToolCallSpec = dict[str, Any]
type _FakeResponse = str | list[_ToolCallSpec]
type _ResponsePair = tuple[str, _FakeResponse]


class FakeChatModel(BaseChatModel):
    """Deterministic fake LLM for testing.

    Takes a list of ``(pattern, response)`` pairs.  On each invocation the
    model scans the pair list in order and returns the response whose pattern
    is a **case-insensitive substring** of the last non-``SystemMessage``
    content.  An empty-string pattern ``""`` always matches and should be
    used as a catch-all placed last in the list.

    Response formats:

    * ``str`` — returned as an ``AIMessage`` with text content.
    * ``list[dict]`` with ``"name"`` keys — each dict is a tool call
      (``"name"`` + ``"args"``); returned as an ``AIMessage`` with
      ``.tool_calls`` populated. ``"id"`` is auto-generated if not provided.
    * ``list[dict]`` **without** ``"name"`` keys — raw content blocks,
      assigned to ``AIMessage.content`` verbatim. Use this to simulate a
      provider that returns list-shaped content, e.g. a Gemini-3 turn that
      spent its whole output budget on reasoning and returned a textless
      signature block ``[{"type": "text", "text": "", "extras": {...}}]``.

    The ``with_structured_output`` method is overridden so that the fake
    can act as the summariser LLM: it parses the response content as JSON
    and constructs the requested Pydantic schema directly.
    """

    responses: list[_ResponsePair] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "fake"

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        response = self._match(messages)
        ai_message = self._build_ai_message(response)
        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    # ------------------------------------------------------------------
    # Structured output override (for summariser use-case)
    # ------------------------------------------------------------------

    def bind_tools(self, tools: Any, **kwargs: Any) -> Any:
        """Accept tool bindings without inspecting them — the fake ignores tools."""
        return self.bind(tools=tools, **kwargs)

    def with_structured_output(self, schema: Any, **kwargs: Any) -> Any:
        """Return a runnable that parses the fake's text content as JSON.

        This allows ``FakeChatModel`` to be used wherever
        ``model.with_structured_output(SomePydanticModel)`` is called —
        without needing real tool-calling infrastructure.  The fake's
        response for that role must be a JSON string whose keys match the
        schema's fields.
        """

        def _parse(ai_message: AIMessage) -> Any:
            data = json.loads(ai_message.content)
            return schema(**data)

        return self | RunnableLambda(_parse)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _match(self, messages: list[BaseMessage]) -> _FakeResponse:
        """Return the response for the first matching pattern.

        Searches the message list from the end, skipping ``SystemMessage``s,
        to find the last substantive message.  Pattern matching is
        case-insensitive substring search.  An empty pattern always matches.
        """
        # Find the last non-system message content.
        last_content = ""
        for msg in reversed(messages):
            if not isinstance(msg, SystemMessage):
                content = msg.content
                if isinstance(content, list):
                    # Handle multimodal content blocks — join text parts.
                    parts = [c["text"] for c in content if isinstance(c, dict) and "text" in c]
                    last_content = " ".join(parts)
                else:
                    last_content = str(content)
                break

        for pattern, response in self.responses:
            if pattern.lower() in last_content.lower():
                return response

        # This should not happen if a catch-all "" pattern is provided,
        # but fall back gracefully to avoid silent test failures.
        if self.responses:
            return self.responses[-1][1]
        return ""

    @staticmethod
    def _build_ai_message(response: _FakeResponse) -> AIMessage:
        """Build an ``AIMessage`` from a string, raw content blocks, or tool calls."""
        if isinstance(response, str):
            return AIMessage(content=response)

        # A non-empty list whose dicts carry no "name" key is raw list-shaped
        # AIMessage content (e.g. a Gemini-3 textless reasoning block), not
        # tool calls. Tool-call specs always carry "name".
        if response and all(isinstance(s, dict) and "name" not in s for s in response):
            return AIMessage(content=list(response))

        tool_calls = []
        for i, spec in enumerate(response):
            tool_calls.append({
                "id": spec.get("id", f"call_{i}"),
                "name": spec["name"],
                "args": spec.get("args", {}),
                "type": "tool_call",
            })
        return AIMessage(content="", tool_calls=tool_calls)
