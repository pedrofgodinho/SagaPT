"""Unit tests for tools.zap_tools._parse_hidden_fields (pure HTML parsing, no live ZAP needed)."""

from tools.zap_tools import _parse_hidden_fields


def test_extracts_hidden_and_submit_inputs():
    html = """
    <form action="login.php" method="post">
      <input type="text" name="username">
      <input type="password" name="password">
      <input type="hidden" name="user_token" value="abc123">
      <input type="submit" name="Login" value="Login">
    </form>
    """
    assert _parse_hidden_fields(html) == {"user_token": "abc123", "Login": "Login"}


def test_text_and_password_inputs_are_not_captured():
    html = """
    <input type="text" name="username" value="ignored">
    <input type="password" name="password" value="ignored">
    """
    assert _parse_hidden_fields(html) == {}


def test_multiple_hidden_fields():
    html = """
    <input type="hidden" name="csrf" value="tok1">
    <input type="HIDDEN" name="session_id" value="tok2">
    """
    assert _parse_hidden_fields(html) == {"csrf": "tok1", "session_id": "tok2"}


def test_hidden_field_without_value_defaults_to_empty_string():
    html = '<input type="hidden" name="empty_token">'
    assert _parse_hidden_fields(html) == {"empty_token": ""}


def test_hidden_field_without_name_is_ignored():
    html = '<input type="hidden" value="orphan">'
    assert _parse_hidden_fields(html) == {}


def test_no_hidden_fields_returns_empty_dict():
    html = "<html><body><p>No forms here.</p></body></html>"
    assert _parse_hidden_fields(html) == {}
