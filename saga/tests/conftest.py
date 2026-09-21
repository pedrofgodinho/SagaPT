"""Shared pytest fixtures for the SagaPT test suite."""

import os

import pytest
import requests as http_requests

# URL used by ZAP (inside Docker) to reach the nginx test site via the Docker network
TEST_SITE_ZAP_URL = "http://test-site"
# URL used by host-side health checks and direct requests (port-mapped)
TEST_SITE_HOST_URL = "http://localhost:8888"
ZAP_TEST_URL = "http://localhost:8080"


def make_alert(
    name: str = "XSS",
    risk: str = "Medium",
    alertid: str = "10",
    url: str = "http://example.com",
    method: str = "GET",
    param: str = "",
    evidence: str = "",
    **kwargs,
) -> dict:
    """Build a minimal ZAP alert dict for use in unit tests."""
    return {
        "alertid": alertid,
        "name": name,
        "risk": risk,
        "confidence": "Medium",
        "cweid": "79",
        "description": "Test description",
        "solution": "Test solution",
        "url": url,
        "method": method,
        "param": param,
        "evidence": evidence,
        **kwargs,
    }


@pytest.fixture(scope="session")
def require_infra():
    """Skip the entire test session if ZAP or the test site is not reachable.

    Run ``just test`` (or ``just test-infra-up``) to start the required services.
    """
    os.environ.setdefault("ZAP_URL", ZAP_TEST_URL)
    os.environ.setdefault("ZAP_API_KEY", "")

    try:
        http_requests.get(f"{ZAP_TEST_URL}/JSON/core/view/version/", timeout=5)
    except Exception:
        pytest.skip(
            "ZAP is not reachable at http://localhost:8080 — run `just test` to start infrastructure."
        )

    try:
        http_requests.get(TEST_SITE_HOST_URL, timeout=5)
    except Exception:
        pytest.skip(
            "Test site is not reachable at http://localhost:8888 — run `just test` to start infrastructure."
        )


@pytest.fixture(scope="session")
def zap_client(require_infra):
    """A ``ZapClient`` wired to the test infra's shared ZAP daemon.

    Integration tests use this instead of the per-run launcher — one ZAP
    for the whole suite is fine because tests are sequential and each
    test uses a distinct ZAP context.
    """
    # Late import: tests that don't need ZAP (unit tests) shouldn't pay the
    # zapv2 import cost or fail on missing deps.
    from tools.zap_tools import ZapClient
    return ZapClient(url=ZAP_TEST_URL, api_key="")


@pytest.fixture(scope="session")
def test_site() -> str:
    """Base URL of the test nginx site, as seen by ZAP inside Docker."""
    return TEST_SITE_ZAP_URL
