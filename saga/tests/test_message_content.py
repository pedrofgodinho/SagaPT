"""Unit tests for graph.message_content and run_manager reasoning/content extraction.

Pure logic — no infrastructure. Guards the emptiness decision that the
agent/planner empty-response nudge relies on, and the reasoning extraction
shown in the trace. The bug these protect against: a Gemini-3 turn that spends
its whole output budget on reasoning returns a *truthy but textless* content
list, which a naive ``bool(message.content)`` check treats as valid output.
"""

from langchain_core.messages import AIMessage

from graph.message_content import extract_text, has_usable_output
from run_manager import _extract_content, _extract_reasoning

# The exact shape langchain-google-genai emits for a Gemini-3 turn that hit
# MAX_TOKENS mid-reasoning: a text block with empty text plus a thought signature.
TEXTLESS_SIGNATURE_BLOCK = [{"type": "text", "text": "", "extras": {"signature": "AY8=="}}]


# --- extract_text -----------------------------------------------------------

def test_extract_text_plain_string():
    assert extract_text("hello world") == "hello world"


def test_extract_text_joins_text_blocks():
    content = [{"type": "text", "text": "foo"}, {"type": "text", "text": "bar"}]
    assert extract_text(content) == "foobar"


def test_extract_text_textless_signature_block_is_empty():
    assert extract_text(TEXTLESS_SIGNATURE_BLOCK) == ""


def test_extract_text_ignores_thinking_blocks():
    content = [{"type": "thinking", "thinking": "reasoning"}, {"type": "text", "text": "answer"}]
    assert extract_text(content) == "answer"


def test_extract_text_non_string_non_list_is_empty():
    assert extract_text(None) == ""


# --- has_usable_output ------------------------------------------------------

def test_has_usable_output_true_for_plain_text():
    assert has_usable_output(AIMessage(content="done")) is True


def test_has_usable_output_true_for_text_block():
    msg = AIMessage(content=[{"type": "text", "text": "found it", "extras": {"signature": "x"}}])
    assert has_usable_output(msg) is True


def test_has_usable_output_true_for_tool_call_even_without_text():
    msg = AIMessage(
        content=TEXTLESS_SIGNATURE_BLOCK,
        tool_calls=[{"name": "http_get", "args": {}, "id": "1", "type": "tool_call"}],
    )
    assert has_usable_output(msg) is True


def test_has_usable_output_false_for_textless_signature_block():
    # The regression: truthy list, no usable text, no tool call → must be empty.
    msg = AIMessage(content=TEXTLESS_SIGNATURE_BLOCK, tool_calls=[])
    assert bool(msg.content) is True  # the trap the old guard fell into
    assert has_usable_output(msg) is False


def test_has_usable_output_false_for_empty_string():
    assert has_usable_output(AIMessage(content="")) is False


def test_has_usable_output_false_for_whitespace_only():
    assert has_usable_output(AIMessage(content="   \n\t")) is False


# --- run_manager._extract_content (delegates to extract_text) ---------------

def test_extract_content_matches_helper_on_textless_block():
    assert _extract_content(AIMessage(content=TEXTLESS_SIGNATURE_BLOCK)) == ""


# --- run_manager._extract_reasoning -----------------------------------------

def test_extract_reasoning_from_thinking_block():
    msg = AIMessage(content=[{"type": "thinking", "thinking": "let me reason"}])
    assert _extract_reasoning(msg) == "let me reason"


def test_extract_reasoning_from_reasoning_block_v1():
    msg = AIMessage(content=[{"type": "reasoning", "reasoning": "v1 thoughts"}])
    assert _extract_reasoning(msg) == "v1 thoughts"


def test_extract_reasoning_from_additional_kwargs():
    msg = AIMessage(content="", additional_kwargs={"reasoning_content": "groq style"})
    assert _extract_reasoning(msg) == "groq style"


def test_extract_reasoning_none_for_textless_signature_block():
    # Reasoning tokens were spent server-side but never returned as content.
    assert _extract_reasoning(AIMessage(content=TEXTLESS_SIGNATURE_BLOCK)) is None


def test_extract_reasoning_none_for_plain_text():
    assert _extract_reasoning(AIMessage(content="just an answer")) is None
