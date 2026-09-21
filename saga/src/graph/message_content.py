"""Helpers for reading usable text out of LLM messages.

Centralising the "is there usable output in this turn?" decision here keeps
the agent/planner empty-response nudge guards and the SSE content extraction
in perfect agreement — if they ever disagree, an empty turn can slip past the
guard while showing as empty in the trace, which is exactly the failure this
module exists to prevent.

**The Gemini-3 gotcha this guards against:** a "thinking" turn that exhausts
its output budget mid-reasoning (``finish_reason == "MAX_TOKENS"``) returns a
content *list* holding a single text block with empty text plus a thought
signature — ``[{"type": "text", "text": "", "extras": {"signature": ...}}]``.
That list is truthy, so a naive ``if message.content`` check treats a turn
with zero usable text and no tool call as valid output. ``has_usable_output``
looks at the extracted text instead, so the nudge actually fires.
"""

from langchain_core.messages import BaseMessage


def extract_text(content: object) -> str:
    """Return the plain-text portion of an LLM message's ``content``.

    Handles both string content (most providers) and list-of-blocks content
    (Gemini 3+, Anthropic), concatenating only ``type == "text"`` blocks and
    ignoring reasoning/thinking blocks and textless signature-only blocks.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def has_usable_output(message: BaseMessage) -> bool:
    """True if *message* carries a tool call or any non-whitespace text.

    This is the correct emptiness guard for the agent/planner nudge: a raw
    ``bool(message.content)`` check is fooled by a non-empty content list that
    holds only a textless thought-signature block (see module docstring),
    treating a genuinely empty turn as valid output and silently ending the
    graph without a nudge.
    """
    if getattr(message, "tool_calls", None):
        return True
    return bool(extract_text(message.content).strip())
