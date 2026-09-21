"""Shared transient-error retry wrapper for LLM calls.

Every LLM call site in the graph (planner, agent, reflect, summarizer) can hit
the same transient provider failures; without a retry they fail the whole run.
This centralises the "is this worth retrying?" decision and the retry loop so
all call sites behave consistently.

**The stuck-model stall this also guards against:** a model occasionally gets
wedged repeating the same sentence forever, so the underlying HTTP request never
completes and ``ainvoke`` never returns — stalling the whole run indefinitely.
There is no exception to catch: the call simply hangs. To recover, every call is
wrapped in a per-call wall-clock timeout (``SAGA_LLM_CALL_TIMEOUT_S``, default
180s; ``<=0`` disables). On timeout the hung call is cancelled and retried like a
transient error; if every attempt times out, the error propagates and the run is
aborted (surfaced as ``FAILED`` by ``stream_run``'s exception handler). This is
distinct from the run-wide ``run_timeout_s`` cap: that bounds the *whole* run,
this unwedges a *single* stuck call so a healthy retry can carry the run forward.

**The google-genai async error-handler crash this guards against:** Vertex AI
Gemini intermittently returns a 5xx ``ServerError``. ``langchain-google-genai``
only wraps ``ClientError`` (4xx) into its own exception, so a ``ServerError``
propagates into ``langchain-core``'s ``BaseChatModel.agenerate`` error path,
which calls ``hasattr(response, "json")`` to attach error metadata. On the
async client, google-genai's ``HttpResponse.json`` property does
``self.response_stream[0]`` — but ``response_stream`` is an aiohttp
``ClientResponse``, not the list it assumes — so it raises
``TypeError: 'ClientResponse' object is not subscriptable``. Because ``hasattr``
only swallows ``AttributeError``, that ``TypeError`` propagates and *replaces*
the original 5xx, failing the run with an inscrutable message. Both the masked
crash and the underlying 5xx are transient, so we retry them.
"""

import asyncio
import logging
import os
from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig

logger = logging.getLogger(__name__)

# Default per-call wall-clock timeout (seconds). A single healthy LLM call —
# even a heavy reasoning turn — finishes well inside this; the ceiling exists
# only to unwedge a call that has stalled (e.g. a model stuck repeating a
# sentence, streaming forever without ever completing). 180s is ~3x the slowest
# real inference observed in practice (~62s, a 35B local model over an 80k-token
# context). Overridable via the ``SAGA_LLM_CALL_TIMEOUT_S`` env var; ``<=0``
# disables the timeout entirely.
_DEFAULT_CALL_TIMEOUT_S = 180.0


def _call_timeout_s() -> float | None:
    """Per-call timeout from ``SAGA_LLM_CALL_TIMEOUT_S`` (``None`` = disabled)."""
    raw = os.getenv("SAGA_LLM_CALL_TIMEOUT_S")
    if raw is None:
        return _DEFAULT_CALL_TIMEOUT_S
    try:
        value = float(raw)
    except ValueError:
        logger.warning(
            "SAGA_LLM_CALL_TIMEOUT_S is not a valid float; using default %ss.",
            _DEFAULT_CALL_TIMEOUT_S,
        )
        return _DEFAULT_CALL_TIMEOUT_S
    return value if value > 0 else None


# Substrings marking a *transient* LLM failure worth retrying rather than
# failing the whole run. Matched case-insensitively against ``str(exc)``.
_RETRYABLE_LLM_ERROR_MARKERS: tuple[str, ...] = (
    # Groq occasionally returns malformed tool-call JSON.
    "failed to parse tool call arguments",
    "parsing failed",
    # The masked google-genai async 5xx crash (see module docstring). This is
    # the concrete signature the run actually fails with, so it must be here.
    "object is not subscriptable",
    # Raw Vertex/Gemini transient server errors, in case a future langchain
    # version surfaces them without the crash above.
    "internal error",
    "'status': 'internal'",
    "service unavailable",
    "'status': 'unavailable'",
    "the model is overloaded",
    "deadline exceeded",
)


def is_retryable_llm_error(exc: BaseException) -> bool:
    """True if *exc* from an LLM call looks transient and worth retrying.

    Covers provider-side blips (malformed tool-call JSON, Vertex 5xx) and the
    google-genai/langchain-core async error-handler crash that masks a 5xx
    (see module docstring). Anything else propagates unchanged.
    """
    msg = str(exc).lower()
    return any(marker in msg for marker in _RETRYABLE_LLM_ERROR_MARKERS)


async def ainvoke_with_retry(
    runnable: Runnable,
    input_: Any,
    config: RunnableConfig,
    *,
    label: str,
    max_retries: int = 3,
    timeout_s: float | None = -1.0,
) -> Any:
    """``await runnable.ainvoke(input_, config=config)`` with retry + timeout.

    Each attempt is bounded by *timeout_s* seconds of wall clock: the default
    sentinel ``-1.0`` reads :func:`_call_timeout_s` (env ``SAGA_LLM_CALL_TIMEOUT_S``),
    while passing ``None`` explicitly disables the timeout. A hung call — e.g. a
    model stuck repeating a sentence, streaming forever without completing — is
    cancelled on timeout and retried like a transient error.

    Retries up to ``max_retries`` attempts, on either a timeout or an error
    matched by :func:`is_retryable_llm_error`, backing off 1s, 2s, … between
    attempts (no backoff after a timeout — the call already burned its budget).
    If every attempt times out the final timeout propagates, aborting the run;
    non-timeout, non-transient errors propagate unchanged so this never hides a
    genuine bug. *label* identifies the call site in the retry log line.
    """
    timeout = _call_timeout_s() if timeout_s == -1.0 else timeout_s
    for attempt in range(max_retries):
        try:
            if timeout is None:
                return await runnable.ainvoke(input_, config=config)
            return await asyncio.wait_for(
                runnable.ainvoke(input_, config=config), timeout=timeout
            )
        except (asyncio.TimeoutError, TimeoutError) as exc:
            # A stalled call (stuck-repeating model, dead connection): cancelled
            # by wait_for. Retry promptly — there is no server error to back off
            # from, and the whole point is to get a fresh, unwedged call going.
            if attempt < max_retries - 1:
                logger.warning(
                    "%s: LLM call timed out after %ss (attempt %d/%d); retrying.",
                    label,
                    timeout,
                    attempt + 1,
                    max_retries,
                )
                continue
            logger.error(
                "%s: LLM call timed out after %ss on the final attempt (%d/%d); "
                "aborting run.",
                label,
                timeout,
                attempt + 1,
                max_retries,
            )
            raise TimeoutError(
                f"{label}: LLM call exceeded {timeout}s on every one of "
                f"{max_retries} attempt(s); the model appears stalled."
            ) from exc
        except Exception as exc:
            if is_retryable_llm_error(exc) and attempt < max_retries - 1:
                delay = 2**attempt  # 1s, 2s, …
                logger.warning(
                    "%s: retryable LLM error (attempt %d/%d, retry in %ds): %s",
                    label,
                    attempt + 1,
                    max_retries,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
            else:
                raise
    raise AssertionError("unreachable")  # loop always returns or raises
