"""Unit tests for graph.subgraph._truncate_body_for_message.

The tool now returns the full response body and the knowledge base stores it
verbatim (``kb.store(json.dumps(raw))``); only the copy echoed back to the agent
in its ToolMessage is capped. These tests lock in that split — most importantly
that the helper never mutates the original ``raw`` dict, so the full body always
survives into the KB regardless of the message-facing truncation.
"""

from graph.subgraph import _MESSAGE_BODY_LIMIT, _truncate_body_for_message


def test_long_body_is_truncated_in_the_returned_copy():
    full_body = "A" * (_MESSAGE_BODY_LIMIT + 5_000)
    raw = {"status": 200, "body": full_body, "alerts": []}

    presented, truncated = _truncate_body_for_message(raw)

    assert truncated is True
    assert len(presented["body"]) == _MESSAGE_BODY_LIMIT
    assert presented["body"] == full_body[:_MESSAGE_BODY_LIMIT]


def test_original_raw_is_never_mutated():
    """The KB persists the original ``raw``; truncation must not touch it."""
    full_body = "B" * (_MESSAGE_BODY_LIMIT + 1)
    raw = {"status": 200, "body": full_body}

    presented, truncated = _truncate_body_for_message(raw)

    assert truncated is True
    assert raw["body"] == full_body  # full body preserved for the KB
    assert presented is not raw  # a distinct copy was returned


def test_body_within_limit_is_returned_unchanged():
    raw = {"status": 200, "body": "short body"}

    presented, truncated = _truncate_body_for_message(raw)

    assert truncated is False
    assert presented is raw  # no copy needed when nothing is trimmed


def test_body_exactly_at_limit_is_not_truncated():
    raw = {"status": 200, "body": "C" * _MESSAGE_BODY_LIMIT}

    presented, truncated = _truncate_body_for_message(raw)

    assert truncated is False
    assert presented is raw


def test_missing_or_nonstring_body_is_left_alone():
    # e.g. spider output, which has no ``body`` field.
    spider_raw = {"discovered_urls": ["/a", "/b"], "alerts": []}
    presented, truncated = _truncate_body_for_message(spider_raw)
    assert truncated is False
    assert presented is spider_raw

    # a defensively non-string body must not raise.
    weird_raw = {"body": None}
    presented, truncated = _truncate_body_for_message(weird_raw)
    assert truncated is False
    assert presented is weird_raw
