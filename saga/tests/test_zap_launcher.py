"""Unit tests for tools/zap_launcher.py.

No docker daemon is required — the ``_run_docker`` helper is monkeypatched
per test.  Focused on the parseable bits: host-port discovery, orphan
sweep behaviour, and readiness-poll timeout.
"""

from __future__ import annotations

import pytest

from tools import zap_launcher


class _FakeResult:
    """Duck-typed stand-in for zap_launcher._RunResult."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.mark.asyncio
async def test_discover_host_port_ipv4(monkeypatch):
    """``docker port <name> 8080`` output like ``0.0.0.0:32768`` returns 32768."""

    async def fake_run(*args, check=True):
        return _FakeResult(returncode=0, stdout="0.0.0.0:32768")

    monkeypatch.setattr(zap_launcher, "_run_docker", fake_run)
    port = await zap_launcher._discover_host_port("sagapt-zap-abc")
    assert port == 32768


@pytest.mark.asyncio
async def test_discover_host_port_ipv6(monkeypatch):
    """``[::]:32768`` also parses to 32768."""

    async def fake_run(*args, check=True):
        return _FakeResult(returncode=0, stdout="[::]:32768")

    monkeypatch.setattr(zap_launcher, "_run_docker", fake_run)
    port = await zap_launcher._discover_host_port("sagapt-zap-abc")
    assert port == 32768


@pytest.mark.asyncio
async def test_discover_host_port_multiple_lines_picks_first_parseable(monkeypatch):
    """When docker prints IPv4 and IPv6 lines, the first parseable one wins."""

    async def fake_run(*args, check=True):
        return _FakeResult(returncode=0, stdout="0.0.0.0:32768\n[::]:32768")

    monkeypatch.setattr(zap_launcher, "_run_docker", fake_run)
    port = await zap_launcher._discover_host_port("sagapt-zap-abc")
    assert port == 32768


@pytest.mark.asyncio
async def test_discover_host_port_no_output_raises(monkeypatch):
    """Empty ``docker port`` output surfaces a clear RuntimeError."""

    async def fake_run(*args, check=True):
        return _FakeResult(returncode=0, stdout="")

    monkeypatch.setattr(zap_launcher, "_run_docker", fake_run)
    with pytest.raises(RuntimeError, match="Could not parse host port"):
        await zap_launcher._discover_host_port("sagapt-zap-abc")


@pytest.mark.asyncio
async def test_sweep_orphans_noop_when_none_present(monkeypatch):
    """``sweep_orphans`` returns quietly when no matching containers exist."""
    calls: list[tuple[str, ...]] = []

    async def fake_run(*args, check=True):
        calls.append(args)
        return _FakeResult(returncode=0, stdout="")

    monkeypatch.setattr(zap_launcher, "_run_docker", fake_run)
    await zap_launcher.sweep_orphans()
    # Only the initial `docker ps -aq --filter label=...` call is made.
    assert len(calls) == 1
    assert calls[0][:2] == ("ps", "-aq")


@pytest.mark.asyncio
async def test_sweep_orphans_removes_found_ids(monkeypatch):
    """When ``docker ps`` returns ids, ``docker rm -f`` is called with all of them."""
    calls: list[tuple[str, ...]] = []

    async def fake_run(*args, check=True):
        calls.append(args)
        if args[0] == "ps":
            return _FakeResult(returncode=0, stdout="abc123\ndef456\n")
        return _FakeResult(returncode=0)

    monkeypatch.setattr(zap_launcher, "_run_docker", fake_run)
    await zap_launcher.sweep_orphans()
    assert len(calls) == 2
    assert calls[1][:2] == ("rm", "-f")
    # Both container ids are passed to the same rm invocation.
    assert "abc123" in calls[1] and "def456" in calls[1]


@pytest.mark.asyncio
async def test_ensure_network_noop_when_exists(monkeypatch):
    """When ``docker network inspect`` succeeds, no create call is issued."""
    calls: list[tuple[str, ...]] = []

    async def fake_run(*args, check=True):
        calls.append(args)
        return _FakeResult(returncode=0, stdout="[]")

    monkeypatch.setattr(zap_launcher, "_run_docker", fake_run)
    await zap_launcher.ensure_network()
    assert len(calls) == 1
    assert calls[0][:2] == ("network", "inspect")


@pytest.mark.asyncio
async def test_ensure_network_creates_when_missing(monkeypatch):
    """When ``inspect`` fails, ``network create`` runs."""
    calls: list[tuple[str, ...]] = []

    async def fake_run(*args, check=True):
        calls.append(args)
        if args[:2] == ("network", "inspect"):
            return _FakeResult(returncode=1, stderr="No such network")
        return _FakeResult(returncode=0)

    monkeypatch.setattr(zap_launcher, "_run_docker", fake_run)
    await zap_launcher.ensure_network()
    assert len(calls) == 2
    assert calls[1][:2] == ("network", "create")
