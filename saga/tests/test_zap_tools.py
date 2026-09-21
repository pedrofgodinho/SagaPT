"""Integration tests for ZAP tools — require a running ZAP + test site.

Start the infrastructure with ``just test`` or ``just test-infra-up``.
"""

import pytest
import requests

from tools.zap_tools import make_zap_tools, setup_zap_context

# All tests in this module require the test infrastructure to be running.
pytestmark = pytest.mark.usefixtures("require_infra")

OUT_OF_SCOPE_URL = "http://example.com/"


@pytest.fixture
def http_get_tool(zap_client, test_site):
    """Return the ``http_get`` tool bound to a fresh session, no context."""
    session = requests.Session()
    tool_map = make_zap_tools(zap_client, session)
    return tool_map["http_get"]


@pytest.fixture
def scoped_tool_map(zap_client, test_site):
    """A tool map restricted to *test_site* only, via ``include``."""
    session = requests.Session()
    return make_zap_tools(zap_client, session, include=[rf"\Q{test_site}\E.*"], exclude=[])


def test_http_get_returns_required_keys(http_get_tool, test_site):
    result = http_get_tool.invoke({"url": test_site, "kb_key": "test"})
    for key in ("status", "headers", "body"):
        assert key in result, f"Missing key: {key}"


def test_http_get_status_200(http_get_tool, test_site):
    result = http_get_tool.invoke({"url": test_site, "kb_key": "test"})
    assert result["status"] == 200


def test_http_get_body_is_html(http_get_tool, test_site):
    result = http_get_tool.invoke({"url": test_site, "kb_key": "test"})
    assert "<html" in result["body"].lower()


def test_http_get_allows_in_scope_url(scoped_tool_map, test_site):
    result = scoped_tool_map["http_get"].invoke({"url": test_site, "kb_key": "test"})
    assert "error" not in result
    assert result["status"] == 200


def test_http_get_blocks_out_of_scope_url(scoped_tool_map):
    result = scoped_tool_map["http_get"].invoke(
        {"url": OUT_OF_SCOPE_URL, "kb_key": "test"}
    )
    assert "error" in result
    assert "outside the allowed scope" in result["error"]


def test_http_post_blocks_out_of_scope_url(scoped_tool_map):
    result = scoped_tool_map["http_post"].invoke(
        {"url": OUT_OF_SCOPE_URL, "data": "{}", "kb_key": "test"}
    )
    assert "error" in result
    assert "outside the allowed scope" in result["error"]


def test_spider_blocks_out_of_scope_seed_url(scoped_tool_map):
    result = scoped_tool_map["spider"].invoke(
        {"url": OUT_OF_SCOPE_URL, "kb_key": "test"}
    )
    assert "error" in result
    assert "outside the allowed scope" in result["error"]


def test_logout_blocks_out_of_scope_url(scoped_tool_map):
    result = scoped_tool_map["logout"].invoke(
        {"logout_url": OUT_OF_SCOPE_URL, "kb_key": "test"}
    )
    assert "error" in result
    assert "outside the allowed scope" in result["error"]


def test_register_credentials_blocks_out_of_scope_login_url(zap_client, test_site):
    session = requests.Session()
    context_id = setup_zap_context(zap_client, "test_scope_ctx", [rf"\Q{test_site}\E.*"], [])
    tool_map = make_zap_tools(
        zap_client, session, context_id, include=[rf"\Q{test_site}\E.*"], exclude=[]
    )
    result = tool_map["register_credentials"].invoke(
        {
            "login_url": OUT_OF_SCOPE_URL,
            "username": "user",
            "password": "pass",
            "kb_key": "test",
        }
    )
    assert "error" in result
    assert "outside the allowed scope" in result["error"]
