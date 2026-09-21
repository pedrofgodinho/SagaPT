"""Unit tests for KnowledgeBase — no infrastructure required."""

import pytest

from knowledge_base import KnowledgeBase


def test_list_keys_empty():
    kb = KnowledgeBase()
    assert kb.list_keys() == []


def test_get_missing_key_returns_none():
    kb = KnowledgeBase()
    assert kb.get("nonexistent") is None


def test_store_and_list_keys():
    kb = KnowledgeBase()
    kb.store("key1", "value one")
    kb.store("key2", "value two")
    assert set(kb.list_keys()) == {"key1", "key2"}


def test_store_preserves_insertion_order():
    kb = KnowledgeBase()
    for i in range(5):
        kb.store(f"k{i}", f"v{i}")
    assert kb.list_keys() == [f"k{i}" for i in range(5)]


def test_store_overwrites_key():
    kb = KnowledgeBase()
    kb.store("dup", "first")
    kb.store("dup", "second")
    assert kb.list_keys() == ["dup"]
    assert kb.get("dup") == "second"


def test_get_existing_key():
    kb = KnowledgeBase()
    kb.store("my_key", "my value")
    assert kb.get("my_key") == "my value"


def test_get_returns_latest_after_overwrite():
    kb = KnowledgeBase()
    kb.store("k", "first")
    kb.store("k", "second")
    assert kb.get("k") == "second"


# ---------------------------------------------------------------------------
# Filesystem persistence
# ---------------------------------------------------------------------------


def test_set_root_flushes_existing_content(tmp_path):
    kb = KnowledgeBase()
    kb.store("recon/tool_logs/get_login.md", "summary text")
    kb.set_root(tmp_path / "kb")
    assert (tmp_path / "kb" / "recon" / "tool_logs" / "get_login.md").read_text() == "summary text"


def test_store_creates_file(tmp_path):
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    kb.store("recon/tool_logs/get_login.md", "summary")
    kb.store("recon/tool_logs/get_login_raw.json", '{"status": 200}')
    assert (tmp_path / "kb" / "recon" / "tool_logs" / "get_login.md").read_text() == "summary"
    assert (tmp_path / "kb" / "recon" / "tool_logs" / "get_login_raw.json").read_text() == '{"status": 200}'


def test_root_not_required():
    """KnowledgeBase works correctly with no backing directory."""
    kb = KnowledgeBase()
    kb.store("x/y.md", "value")
    assert kb.get("x/y.md") == "value"


# ---------------------------------------------------------------------------
# list_dir
# ---------------------------------------------------------------------------


def test_list_dir_root_in_memory():
    kb = KnowledgeBase()
    kb.store("recon/tool_logs/a.md", "1")
    kb.store("recon/tool_logs/b.md", "2")
    kb.store("dast/tool_logs/c.md", "3")
    assert sorted(kb.list_dir("")) == ["dast", "recon"]


def test_list_dir_subdir_in_memory():
    kb = KnowledgeBase()
    kb.store("recon/tool_logs/a.md", "1")
    kb.store("recon/tool_logs/b_raw.json", "2")
    assert sorted(kb.list_dir("recon/tool_logs")) == ["a.md", "b_raw.json"]


def test_list_dir_empty_when_no_keys():
    kb = KnowledgeBase()
    assert kb.list_dir("") == []


def test_list_dir_filesystem(tmp_path):
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    kb.store("recon/tool_logs/get_login.md", "s")
    kb.store("recon/tool_logs/get_login_raw.json", "{}")
    assert sorted(kb.list_dir("recon/tool_logs")) == ["get_login.md", "get_login_raw.json"]
    assert kb.list_dir("recon") == ["tool_logs"]
    assert kb.list_dir("") == ["recon"]


def test_list_dir_path_traversal_rejected(tmp_path):
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    with pytest.raises(ValueError, match="traversal"):
        kb.list_dir("../secret")


# ---------------------------------------------------------------------------
# register_finding
# ---------------------------------------------------------------------------


def test_register_finding_stores_file(tmp_path):
    from tools.kb_tools import make_kb_tools
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    tools = {t.name: t for t in make_kb_tools(kb, "recon")}
    result = tools["register_finding"].invoke({"title": "SQL Injection Login", "content": "# SQLi\nConfirmed."})
    assert "recon/findings/sql_injection_login.md" in result
    assert (tmp_path / "kb" / "recon" / "findings" / "sql_injection_login.md").read_text() == "# SQLi\nConfirmed."


def test_register_finding_scoped_to_agent(tmp_path):
    """register_finding always writes under its own agent directory."""
    from tools.kb_tools import make_kb_tools
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    recon_tools = {t.name: t for t in make_kb_tools(kb, "recon")}
    dast_tools = {t.name: t for t in make_kb_tools(kb, "dast")}
    recon_tools["register_finding"].invoke({"title": "login form", "content": "found it"})
    dast_tools["register_finding"].invoke({"title": "xss search", "content": "confirmed"})
    assert (tmp_path / "kb" / "recon" / "findings" / "login_form.md").exists()
    assert (tmp_path / "kb" / "dast" / "findings" / "xss_search.md").exists()


def test_register_finding_rejects_duplicate_title(tmp_path):
    """A second register_finding with the same title errors instead of overwriting."""
    from tools.kb_tools import make_kb_tools
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    tools = {t.name: t for t in make_kb_tools(kb, "dast")}
    tools["register_finding"].invoke({"title": "SQL Injection Search", "content": "first version"})
    result = tools["register_finding"].invoke({"title": "SQL Injection Search", "content": "second version"})
    assert "Error" in result
    assert "already exists" in result
    assert (tmp_path / "kb" / "dast" / "findings" / "sql_injection_search.md").read_text() == "first version"


def test_register_finding_path_traversal_in_title(tmp_path):
    """A title containing path separators is fully sanitized."""
    from tools.kb_tools import make_kb_tools
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    tools = {t.name: t for t in make_kb_tools(kb, "recon")}
    result = tools["register_finding"].invoke({"title": "../../../etc/passwd", "content": "evil"})
    # Slug strips the traversal characters; file lands safely under recon/findings/
    assert "recon/findings/" in result
    assert ".." not in result


def test_kb_get_returns_small_entry_verbatim(tmp_path):
    """An entry within the read limit is returned unchanged, no notice prepended."""
    from tools.kb_tools import make_kb_tools, _KB_GET_CHAR_LIMIT
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    kb.store("recon/small.md", "hello world")
    tools = {t.name: t for t in make_kb_tools(kb, "recon")}
    result = tools["kb_get"].invoke({"key": "recon/small.md"})
    assert result == "hello world"
    assert "too large" not in result


def test_kb_get_truncates_oversized_entry(tmp_path):
    """An entry above the read limit is truncated to it and prefixed with a notice.

    Guards the failure mode that killed the Juice Shop run: recon fetched a 1.2 MB
    JS bundle, whose full body the KB stored, then kb_get returned it whole and
    blew past the model's context window. kb_get must cap what it hands back.
    """
    from tools.kb_tools import make_kb_tools, _KB_GET_CHAR_LIMIT
    kb = KnowledgeBase()
    kb.set_root(tmp_path / "kb")
    big = "A" * (_KB_GET_CHAR_LIMIT * 3)
    kb.store("recon/initial_recon/tool_logs/main_js_source_raw.json", big)
    tools = {t.name: t for t in make_kb_tools(kb, "recon")}
    result = tools["kb_get"].invoke(
        {"key": "recon/initial_recon/tool_logs/main_js_source_raw.json"}
    )
    # Notice announces the truncation and the true full size.
    assert "too large to return in full" in result
    assert str(len(big)) in result
    # The returned content payload (after the notice) is capped at the limit.
    payload = result.split("\n\n", 1)[1]
    assert len(payload) == _KB_GET_CHAR_LIMIT
    assert payload == big[:_KB_GET_CHAR_LIMIT]
    # The full entry is untouched in the store.
    assert kb.get("recon/initial_recon/tool_logs/main_js_source_raw.json") == big
