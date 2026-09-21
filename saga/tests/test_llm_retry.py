"""Unit tests for graph.llm_retry — transient-error detection and retry loop.

Pure logic; no live provider. Guards the retry that keeps a transient Vertex
5xx (and the masked google-genai async error-handler crash it surfaces as)
from failing a whole run.
"""

import asyncio

import pytest

from graph.llm_retry import (
    _call_timeout_s,
    ainvoke_with_retry,
    is_retryable_llm_error,
)


# --- is_retryable_llm_error -------------------------------------------------

@pytest.mark.parametrize("msg", [
    "'ClientResponse' object is not subscriptable",   # the reported masked 5xx crash
    "Failed to parse tool call arguments for foo",     # Groq
    "Parsing failed: bad JSON",                        # Groq
    "500 INTERNAL. {'error': {'code': 500, 'status': 'INTERNAL'}}",
    "503 Service Unavailable",
    "The model is overloaded. Please try again later.",
    "504 Deadline Exceeded",
])
def test_retryable_errors(msg):
    assert is_retryable_llm_error(Exception(msg)) is True


@pytest.mark.parametrize("msg", [
    "429 Too Many Requests",          # rate limit — handled by SDK retry, not here
    "KeyError: 'target'",             # genuine bug in our code
    "Some ValueError we wrote",
    "401 Unauthorized",
])
def test_non_retryable_errors(msg):
    assert is_retryable_llm_error(Exception(msg)) is False


# --- ainvoke_with_retry -----------------------------------------------------

class _FlakyRunnable:
    """Fake Runnable that raises *exc* for the first *fail_times* calls."""

    def __init__(self, fail_times: int, exc: Exception, result="ok"):
        self.fail_times = fail_times
        self.exc = exc
        self.result = result
        self.calls = 0

    async def ainvoke(self, input_, config=None):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.exc
        return self.result


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Skip the backoff sleeps so retry tests run instantly."""
    async def _instant(_seconds):
        return None
    monkeypatch.setattr(asyncio, "sleep", _instant)


async def test_recovers_after_transient_error():
    r = _FlakyRunnable(fail_times=2, exc=TypeError("'ClientResponse' object is not subscriptable"))
    out = await ainvoke_with_retry(r, "in", {}, label="test", max_retries=3)
    assert out == "ok"
    assert r.calls == 3  # failed twice, succeeded on the third


async def test_gives_up_after_max_retries_and_reraises():
    err = TypeError("'ClientResponse' object is not subscriptable")
    r = _FlakyRunnable(fail_times=99, exc=err)
    with pytest.raises(TypeError, match="not subscriptable"):
        await ainvoke_with_retry(r, "in", {}, label="test", max_retries=3)
    assert r.calls == 3  # exactly max_retries attempts, no more


async def test_non_retryable_error_propagates_immediately():
    err = KeyError("target")
    r = _FlakyRunnable(fail_times=99, exc=err)
    with pytest.raises(KeyError):
        await ainvoke_with_retry(r, "in", {}, label="test", max_retries=3)
    assert r.calls == 1  # no retry for a non-transient error


async def test_succeeds_first_try_no_retry():
    r = _FlakyRunnable(fail_times=0, exc=Exception("unused"))
    out = await ainvoke_with_retry(r, "in", {}, label="test")
    assert out == "ok"
    assert r.calls == 1


# --- per-call timeout (stuck-model stall) -----------------------------------

class _HangingRunnable:
    """Fake Runnable that hangs forever for the first *hang_times* calls.

    Models the stall we guard against: a call that never completes (e.g. a
    model stuck repeating a sentence, streaming without end). ``Event().wait()``
    blocks until the surrounding ``wait_for`` cancels it — real wall-clock time,
    unaffected by the ``_no_sleep`` fixture (``wait_for`` uses ``call_later``).
    """

    def __init__(self, hang_times: int, result="ok"):
        self.hang_times = hang_times
        self.result = result
        self.calls = 0

    async def ainvoke(self, input_, config=None):
        self.calls += 1
        if self.calls <= self.hang_times:
            await asyncio.Event().wait()  # hang until cancelled by the timeout
        return self.result


async def test_recovers_after_timeout_stall():
    r = _HangingRunnable(hang_times=2)
    out = await ainvoke_with_retry(
        r, "in", {}, label="test", max_retries=3, timeout_s=0.05
    )
    assert out == "ok"
    assert r.calls == 3  # timed out twice, succeeded on the third


async def test_aborts_after_all_attempts_time_out():
    r = _HangingRunnable(hang_times=99)
    with pytest.raises(TimeoutError, match="stalled"):
        await ainvoke_with_retry(
            r, "in", {}, label="test", max_retries=3, timeout_s=0.05
        )
    assert r.calls == 3  # exactly max_retries attempts, no more


async def test_timeout_disabled_lets_slow_call_complete():
    # timeout_s=None disables the wall-clock cap: a call slower than any tiny
    # threshold still completes instead of being cancelled.
    r = _HangingRunnable(hang_times=0)
    out = await ainvoke_with_retry(r, "in", {}, label="test", timeout_s=None)
    assert out == "ok"
    assert r.calls == 1


# --- _call_timeout_s (env parsing) ------------------------------------------

def test_call_timeout_default(monkeypatch):
    monkeypatch.delenv("SAGA_LLM_CALL_TIMEOUT_S", raising=False)
    assert _call_timeout_s() == 180.0


def test_call_timeout_override(monkeypatch):
    monkeypatch.setenv("SAGA_LLM_CALL_TIMEOUT_S", "42")
    assert _call_timeout_s() == 42.0


@pytest.mark.parametrize("value", ["0", "-5"])
def test_call_timeout_disabled(monkeypatch, value):
    monkeypatch.setenv("SAGA_LLM_CALL_TIMEOUT_S", value)
    assert _call_timeout_s() is None


def test_call_timeout_invalid_falls_back(monkeypatch):
    monkeypatch.setenv("SAGA_LLM_CALL_TIMEOUT_S", "not-a-number")
    assert _call_timeout_s() == 180.0
