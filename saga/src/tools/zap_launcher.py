"""Per-run ZAP container lifecycle.

Each SagaPT run gets its own ephemeral ZAP daemon so N concurrent runs share
no ZAP state.  ``start_zap`` launches a container labeled with the run id and
returns a ready-to-use ``ZapClient``; ``stop_zap`` tears it down.  ``sweep_orphans``
removes any leftover labeled containers at API server boot to recover from
crashes.

All docker interaction goes through the CLI via
``asyncio.create_subprocess_exec`` — mirroring the pattern already used by
``xbow/runner.py``.  No new dependency (docker-py, etc.) is introduced.

The container is joined to the ``saga-net`` bridge so it can reach targets
that publish aliases on that network (Hackergram, DVWA); ``host.docker.internal``
resolves to the host gateway for XBOW benchmark stacks published on the host.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass

import requests

from tools.zap_tools import ZapClient

logger = logging.getLogger(__name__)

# Image + infra configuration (env-overridable for dev flexibility).
_IMAGE = os.getenv("SAGAPT_ZAP_IMAGE", "zaproxy/zap-stable")
_NETWORK = os.getenv("SAGAPT_ZAP_NETWORK", "saga-net")
_HOST_BIND = os.getenv("SAGAPT_ZAP_HOST_BIND", "127.0.0.1")
_STARTUP_TIMEOUT = int(os.getenv("SAGAPT_ZAP_STARTUP_TIMEOUT", "60"))
_API_KEY = os.getenv("ZAP_API_KEY", "")  # empty → daemon runs with api.disablekey=true

# Labels used to identify our containers for cleanup.
_LABEL_ROLE = "sagapt.role=zap"
_LABEL_RUN = "sagapt.run_id"


@dataclass(frozen=True)
class _RunResult:
    """Result of a ``docker`` invocation."""

    returncode: int
    stdout: str
    stderr: str


async def _run_docker(*args: str, check: bool = True) -> _RunResult:
    """Invoke ``docker`` with the given args, capturing stdout/stderr.

    Raises ``RuntimeError`` on non-zero exit when ``check`` is true.
    """
    proc = await asyncio.create_subprocess_exec(
        "docker",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_bytes, stderr_bytes = await proc.communicate()
    stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
    stderr = stderr_bytes.decode("utf-8", errors="replace").strip()
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"docker {' '.join(args)} failed (exit {proc.returncode}): {stderr}"
        )
    assert proc.returncode is not None
    return _RunResult(proc.returncode, stdout, stderr)


def _container_name(run_id: str) -> str:
    """Deterministic container name for a run id."""
    # Docker names allow [a-zA-Z0-9][a-zA-Z0-9_.-]* — run ids are already safe.
    return f"sagapt-zap-{run_id}"


async def start_zap(run_id: str) -> ZapClient:
    """Launch a dedicated ZAP container for *run_id* and return its client.

    Publishes ZAP's daemon port to an OS-assigned host port so N concurrent
    runs never collide.  Blocks until the daemon responds to
    ``/JSON/core/view/version/`` or the startup timeout is hit.
    """
    name = _container_name(run_id)
    daemon_cmd = [
        "zap.sh",
        "-daemon",
        "-host", "0.0.0.0",
        "-port", "8080",
        "-config", "api.addrs.addr.name=.*",
        "-config", "api.addrs.addr.regex=true",
    ]
    if _API_KEY:
        daemon_cmd.extend(["-config", f"api.key={_API_KEY}"])
    else:
        daemon_cmd.extend(["-config", "api.disablekey=true"])

    logger.info("Starting per-run ZAP container '%s' (image=%s).", name, _IMAGE)
    await _run_docker(
        "run", "-d",
        "--name", name,
        "--label", _LABEL_ROLE,
        "--label", f"{_LABEL_RUN}={run_id}",
        "--network", _NETWORK,
        "--add-host", "host.docker.internal:host-gateway",
        "-p", f"{_HOST_BIND}:0:8080",
        _IMAGE,
        *daemon_cmd,
    )

    try:
        port = await _discover_host_port(name)
        url = f"http://{_HOST_BIND}:{port}"
        await _wait_for_ready(url)
    except Exception:
        # Best-effort teardown so a failed start never leaks a container.
        logger.warning("ZAP startup failed for '%s'; removing container.", name)
        await _run_docker("rm", "-f", name, check=False)
        raise

    logger.info("ZAP container '%s' ready at %s.", name, url)
    return ZapClient(url=url, api_key=_API_KEY)


async def stop_zap(zap: ZapClient, run_id: str) -> None:
    """Force-remove the ZAP container that backs *zap* (best-effort).

    ``run_id`` is used to derive the container name — the ``ZapClient`` itself
    only knows the URL.  Failures are logged and swallowed: a wedged container
    can be cleaned up later by ``sweep_orphans`` at server boot.
    """
    name = _container_name(run_id)
    logger.info("Stopping ZAP container '%s' (url=%s).", name, zap.url)
    result = await _run_docker("rm", "-f", name, check=False)
    if result.returncode != 0:
        logger.warning(
            "Failed to remove ZAP container '%s': %s (will be swept on next server boot).",
            name, result.stderr,
        )


async def ensure_network() -> None:
    """Create the ``saga-net`` bridge if it does not exist (idempotent).

    Per-run ZAP containers need this network to join.  It is normally created
    by ``docker compose up`` for the target stack, but starting the API
    server before running ``just infra-up`` would otherwise fail on the
    first ``start_zap`` with a confusing "network not found" error.
    """
    inspect = await _run_docker("network", "inspect", _NETWORK, check=False)
    if inspect.returncode == 0:
        return
    logger.info("Creating docker network '%s' (did not exist).", _NETWORK)
    await _run_docker("network", "create", _NETWORK, check=False)


async def sweep_orphans() -> None:
    """Remove any leftover ``sagapt.role=zap`` containers.

    Called from the API server's ``lifespan`` at boot so a previous crash
    doesn't leave zombie containers eating memory or holding host ports.
    """
    result = await _run_docker(
        "ps", "-aq", "--filter", f"label={_LABEL_ROLE}", check=False,
    )
    if result.returncode != 0:
        logger.warning("sweep_orphans: docker ps failed: %s", result.stderr)
        return
    ids = [line for line in result.stdout.splitlines() if line.strip()]
    if not ids:
        logger.debug("sweep_orphans: no orphan ZAP containers.")
        return
    logger.info("sweep_orphans: removing %d orphan ZAP container(s).", len(ids))
    await _run_docker("rm", "-f", *ids, check=False)


async def _discover_host_port(name: str) -> int:
    """Return the host port docker mapped to container port 8080."""
    # `docker port <name> 8080` prints one line per binding, e.g. "0.0.0.0:32768"
    # or "127.0.0.1:32768".  On Windows/mac it may also print IPv6 bindings.
    result = await _run_docker("port", name, "8080")
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # Take the last ":<port>" — handles IPv4 ("127.0.0.1:32768") and IPv6
        # ("[::]:32768") uniformly.
        try:
            return int(line.rsplit(":", 1)[-1])
        except ValueError:
            continue
    raise RuntimeError(
        f"Could not parse host port from `docker port {name} 8080` output: {result.stdout!r}"
    )


async def _wait_for_ready(url: str) -> None:
    """Poll the ZAP version endpoint until it responds or the timeout expires.

    Uses the proxy-tunnel pattern (``proxies={"http": url, ...}`` + magic
    ``http://zap/`` hostname) rather than a direct hit on the discovered
    port.  A direct hit would send ``Host: 127.0.0.1:<random>`` — ZAP's
    JSON API only answers direct requests when the Host-header port matches
    its internal ``-port 8080``, and otherwise treats the request as a
    forward-proxy attempt and returns a misleading error body (see the
    "ZAP Direct API Access Requires Matching Port" note).  OS-assigned host
    ports never match 8080, so the direct pattern would falsely time out
    even on a perfectly healthy ZAP.
    """
    proxies = {"http": url, "https": url}
    version_url = "http://zap/JSON/core/view/version/"
    deadline = time.monotonic() + _STARTUP_TIMEOUT
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            # ZAP is heavy; give each probe generous budget but don't block the loop.
            response = await asyncio.to_thread(
                requests.get, version_url, proxies=proxies, timeout=3,
            )
            if response.status_code == 200:
                return
            last_error = RuntimeError(
                f"ZAP responded with HTTP {response.status_code} at {version_url}"
            )
        except requests.RequestException as exc:
            last_error = exc
        await asyncio.sleep(0.5)
    raise TimeoutError(
        f"ZAP daemon at {url} did not become ready within {_STARTUP_TIMEOUT}s"
        + (f" (last error: {last_error})" if last_error else "")
    )
