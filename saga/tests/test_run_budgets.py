"""Tests for run budgets: token accounting + TokenBudgetExceeded enforcement.

The wall-clock cap is exercised end-to-end in ``test_api_events.py`` via a
tiny ``run_timeout_s`` value; the token accounting primitive is unit-tested
here because the FakeChatModel used elsewhere doesn't emit
``usage_metadata`` and wiring one that does would balloon test setup.
"""

import pytest

from run_manager import (
    RunState,
    RunStatus,
    TokenBudgetExceeded,
    _account_usage,
)


def _empty_run_state() -> RunState:
    """Minimal RunState for accounting tests."""
    from datetime import datetime, timezone
    return RunState(
        run_id="test-run",
        name="test",
        status=RunStatus.RUNNING,
        target="http://fake",
        started_at=datetime.now(timezone.utc),
        ended_at=None,
        kb=None,
    )


def test_account_usage_increments_running_total():
    run = _empty_run_state()
    assert run.total_tokens == 0
    _account_usage(run, {"total_tokens": 500}, token_budget=None)
    assert run.total_tokens == 500
    _account_usage(run, {"total_tokens": 300}, token_budget=None)
    assert run.total_tokens == 800


def test_account_usage_handles_none_usage():
    """AI events without usage metadata (e.g. fake models) must not crash."""
    run = _empty_run_state()
    _account_usage(run, None, token_budget=100)
    assert run.total_tokens == 0


def test_account_usage_handles_missing_total_tokens_key():
    run = _empty_run_state()
    _account_usage(run, {"input_tokens": 50}, token_budget=100)  # no total_tokens
    assert run.total_tokens == 0


def test_account_usage_handles_zero_total_tokens():
    run = _empty_run_state()
    _account_usage(run, {"total_tokens": 0}, token_budget=100)
    assert run.total_tokens == 0


def test_no_budget_never_raises():
    run = _empty_run_state()
    for _ in range(1000):
        _account_usage(run, {"total_tokens": 1000}, token_budget=None)
    assert run.total_tokens == 1_000_000  # 1M tokens, no exception raised


def test_zero_or_negative_budget_never_raises():
    """A budget of 0 or negative is treated as 'disabled', matching saga.toml docs."""
    run = _empty_run_state()
    _account_usage(run, {"total_tokens": 10**9}, token_budget=0)
    _account_usage(run, {"total_tokens": 10**9}, token_budget=-1)
    # Total accumulates but no exception.
    assert run.total_tokens == 2 * 10**9


def test_budget_hit_raises_with_diagnostic():
    run = _empty_run_state()
    _account_usage(run, {"total_tokens": 90}, token_budget=100)  # under
    with pytest.raises(TokenBudgetExceeded) as excinfo:
        _account_usage(run, {"total_tokens": 20}, token_budget=100)  # crosses
    assert excinfo.value.total == 110
    assert excinfo.value.budget == 100
    assert "110" in str(excinfo.value)
    assert "100" in str(excinfo.value)


def test_budget_at_exact_limit_does_not_raise():
    """Total *equal* to the budget is allowed; only *exceeding* raises."""
    run = _empty_run_state()
    _account_usage(run, {"total_tokens": 100}, token_budget=100)
    assert run.total_tokens == 100  # no exception at the exact limit


def test_budget_barely_exceeded_raises():
    run = _empty_run_state()
    with pytest.raises(TokenBudgetExceeded):
        _account_usage(run, {"total_tokens": 101}, token_budget=100)
