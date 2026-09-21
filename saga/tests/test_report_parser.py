"""Unit tests for report_parser.parse_findings_table."""

from report_parser import parse_findings_table


def test_well_formed_table():
    report = """\
## Findings Summary

| Endpoint | Vulnerability | PoC |
| --- | --- | --- |
| /login | SQL Injection | `' OR '1'='1' -- ` |
| /search?q= | SQL Injection | `' UNION SELECT username, password FROM users -- ` |
"""
    findings = parse_findings_table(report)
    assert findings == [
        {
            "endpoint": "/login",
            "vulnerability": "SQL Injection",
            "poc": "`' OR '1'='1' -- `",
        },
        {
            "endpoint": "/search?q=",
            "vulnerability": "SQL Injection",
            "poc": "`' UNION SELECT username, password FROM users -- `",
        },
    ]


def test_table_embedded_among_other_sections():
    report = """\
# Final Report

## Critical
- SQL injection on /login allows authentication bypass.

## Coverage gaps
- Could not test the /admin panel.

## Findings Summary

| Endpoint | Vulnerability | PoC |
|---|---|---|
| /login | SQL Injection | admin' -- |

Thanks for reading.
"""
    findings = parse_findings_table(report)
    assert findings == [
        {"endpoint": "/login", "vulnerability": "SQL Injection", "poc": "admin' --"},
    ]


def test_no_table_returns_empty_list():
    report = "## Findings\nNo vulnerabilities were confirmed during this engagement.\n"
    assert parse_findings_table(report) == []


def test_missing_poc_column_defaults_to_empty_string():
    report = """\
| Endpoint | Vulnerability |
| --- | --- |
| /login | SQL Injection |
"""
    findings = parse_findings_table(report)
    assert findings == [
        {"endpoint": "/login", "vulnerability": "SQL Injection", "poc": ""},
    ]


def test_case_insensitive_and_reordered_headers():
    report = """\
| PoC | Endpoint | Vulnerability |
| --- | --- | --- |
| ' OR 1=1 -- | /search | sql injection |
"""
    findings = parse_findings_table(report)
    assert findings == [
        {"endpoint": "/search", "vulnerability": "sql injection", "poc": "' OR 1=1 --"},
    ]
