"""CLI harness for launching the same run configuration multiple times, sequentially.

Used to gather replicability data: the exact same target + prompt configuration
(fetched once from ``GET /api/v1/config``) is POSTed to the API server N times
in a row, each run named ``"{name} #{n}"`` so the frontend, SSE history, and
``saga_runs/`` are trivially groupable by attempt number. Talks to an
already-running API server over HTTP — the same host-side pattern used by the
XBOW harness (``xbow/runner.py``).
"""

import logging
import subprocess
import sys
import time

import requests

logger = logging.getLogger(__name__)

API_BASE = "http://127.0.0.1:8080"
POLL_INTERVAL_S = 10
RESET_TIMEOUT_S = 120
_TERMINAL_STATUSES = frozenset({"completed", "cancelled", "failed"})


def _reset_container(container: str, timeout: float) -> None:
    """Restart *container* and block until Docker reports it healthy again.

    Hackergram (like DVWA) reseeds its database from a committed SQL script
    on every container start (``container_start.sh`` runs ``mysql -u root <
    start.sql``, which ``DROP DATABASE IF EXISTS``s first) — so a plain
    ``docker restart`` is enough to discard whatever an agent mutated during
    the previous run (created users/posts/friend requests, stored XSS
    payloads, ...) and get back to the same seeded state, without a full
    image rebuild or volume wipe. If the container defines no
    ``HEALTHCHECK`` (``docker inspect`` errors on ``.State.Health``), falls
    back to a short fixed grace period for the entrypoint to finish booting.
    """
    result = subprocess.run(
        ["docker", "restart", container], capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"docker restart {container} failed: {result.stderr.strip()}")

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", container],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            # No HEALTHCHECK defined for this container -- best-effort grace period.
            time.sleep(5)
            return
        status = result.stdout.strip()
        if status == "healthy":
            return
        if status == "unhealthy":
            raise RuntimeError(f"container '{container}' reported unhealthy after restart.")
        time.sleep(2)
    raise TimeoutError(f"container '{container}' did not become healthy within {timeout}s of restart.")


def _fetch_base_config(api_base: str) -> dict:
    """Fetch the default run configuration (target, prompts, agents) from the API server."""
    resp = requests.get(f"{api_base}/api/v1/config", timeout=10)
    resp.raise_for_status()
    return resp.json()


def _start_run(config: dict, api_base: str) -> str:
    """POST /api/v1/runs and return the new run's ``run_id``."""
    resp = requests.post(f"{api_base}/api/v1/runs", json=config, timeout=30)
    resp.raise_for_status()
    return str(resp.json()["run_id"])


def _poll_until_done(run_id: str, api_base: str, poll_interval: float) -> dict:
    """Poll ``GET /api/v1/runs/{run_id}`` until it reaches a terminal status."""
    while True:
        resp = requests.get(f"{api_base}/api/v1/runs/{run_id}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data["status"] in _TERMINAL_STATUSES:
            return data
        time.sleep(poll_interval)


def run_replication(
    *,
    start: int,
    end: int,
    name: str,
    api_base: str = API_BASE,
    poll_interval: float = POLL_INTERVAL_S,
    reset_container: str | None = None,
    reset_timeout: float = RESET_TIMEOUT_S,
) -> None:
    """Launch runs ``"{name} #{start}"`` through ``"{name} #{end}"``, one at a time.

    Every run reuses the exact same base configuration fetched once from
    ``GET /api/v1/config`` — only the ``name`` field changes — so the batch is
    a replicability check (identical target/prompt/agent setup, run N times)
    rather than N distinct configurations. Runs execute strictly
    sequentially: each is started and polled to completion before the next is
    launched.

    If *reset_container* is given (a docker container name, e.g.
    ``hackergram_target``), it is restarted and waited on to become healthy
    before *every* run in the batch, including the first — so each attempt
    starts from the same freshly-seeded target state rather than whatever an
    agent left behind on the previous attempt. A reset failure aborts the
    whole batch immediately rather than continuing against unreset state,
    since the resulting run would silently invalidate the replicability
    comparison.
    """
    if start > end:
        print(f"error: --start ({start}) must be <= --end ({end}).", file=sys.stderr)
        sys.exit(1)

    base_config = _fetch_base_config(api_base)
    total = end - start + 1
    print(f"Replicating '{name}' as runs #{start}-#{end} ({total} total) against {api_base}.\n")

    completed = 0
    failures: list[str] = []
    for i, n in enumerate(range(start, end + 1), start=1):
        run_name = f"{name} #{n}"
        config = dict(base_config)
        config["name"] = run_name

        if reset_container:
            print(f"[{i}/{total}] {run_name} -> resetting '{reset_container}'...")
            try:
                _reset_container(reset_container, reset_timeout)
            except (RuntimeError, TimeoutError, subprocess.SubprocessError) as exc:
                print(f"[{i}/{total}] {run_name} -> RESET FAILED: {exc}", file=sys.stderr)
                print(f"\nAborting batch after {completed}/{total} completed (target reset failed).")
                sys.exit(1)

        t0 = time.monotonic()
        try:
            run_id = _start_run(config, api_base)
        except requests.RequestException as exc:
            print(f"[{i}/{total}] {run_name} -> FAILED TO START: {exc}")
            failures.append(run_name)
            continue

        print(f"[{i}/{total}] {run_name} -> started (run_id={run_id}), waiting...")
        try:
            result = _poll_until_done(run_id, api_base, poll_interval)
        except requests.RequestException as exc:
            print(f"[{i}/{total}] {run_name} -> ERROR WHILE POLLING: {exc}")
            failures.append(run_name)
            continue

        duration = time.monotonic() - t0
        status = result["status"]
        if status == "completed":
            completed += 1
        else:
            failures.append(run_name)
        error_suffix = f" ({result['error']})" if result.get("error") else ""
        print(f"[{i}/{total}] {run_name} -> {status.upper()}{error_suffix} in {duration:.0f}s")

    print(f"\nDone. {completed}/{total} completed.")
    if failures:
        print(f"Not completed: {', '.join(failures)}")
