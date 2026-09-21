"""Unit tests for tools.url_scope (pure string/regex logic, no live ZAP needed)."""

from tools.url_scope import make_scope_checker


def test_no_include_means_unrestricted():
    check = make_scope_checker(include=[], exclude=[])
    assert check("http://anything.example.com/path") is None
    assert check("http://169.254.169.254/latest/meta-data/") is None


def test_none_include_and_exclude_means_unrestricted():
    check = make_scope_checker(include=None, exclude=None)
    assert check("http://anything.example.com/") is None


def test_qe_literal_prefix_allows_matching_url():
    check = make_scope_checker(
        include=[r"\Qhttp://www.hackergram.com\E.*"], exclude=[]
    )
    assert check("http://www.hackergram.com/login") is None


def test_qe_literal_prefix_blocks_other_hosts():
    check = make_scope_checker(
        include=[r"\Qhttp://www.hackergram.com\E.*"], exclude=[]
    )
    error = check("http://169.254.169.254/latest/meta-data/")
    assert error is not None
    assert "outside the allowed scope" in error


def test_qe_literal_prefix_without_wildcard_suffix():
    check = make_scope_checker(include=[r"\Qhttp://dvwa.local\E"], exclude=[])
    assert check("http://dvwa.local") is None
    assert check("http://dvwa.local/login.php") is not None


def test_multiple_include_patterns_any_match_allows():
    check = make_scope_checker(
        include=[
            r"\Qhttp://www.hackergram.com\E.*",
            r"\Qhttp://hackergram.com\E.*",
        ],
        exclude=[],
    )
    assert check("http://www.hackergram.com/") is None
    assert check("http://hackergram.com/") is None
    assert check("http://evil.example.com/") is not None


def test_exclude_wins_over_include():
    check = make_scope_checker(
        include=[r"\Qhttp://dvwa.local\E.*"],
        exclude=[r"\Qhttp://dvwa.local/logout.php\E"],
    )
    assert check("http://dvwa.local/index.php") is None
    error = check("http://dvwa.local/logout.php")
    assert error is not None
    assert "excluded" in error


def test_plain_python_regex_pattern_still_works():
    check = make_scope_checker(include=[r"http://target:\d+/.*"], exclude=[])
    assert check("http://target:5000/app") is None
    assert check("http://other:5000/app") is not None


def test_malformed_pattern_falls_back_to_literal_prefix_without_crashing():
    # "(" is an unbalanced group -> invalid Python regex; must not raise.
    check = make_scope_checker(include=["http://example.com/("], exclude=[])
    assert check("http://example.com/(rest") is None
    assert check("http://example.com/other") is not None
