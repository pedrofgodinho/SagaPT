"""Parsing utilities for the planner's final report.

The planner is instructed (see ``prompts/planner/system.md``) to end its
final report with a "Findings Summary" markdown table whose columns are
``Endpoint``, ``Vulnerability``, and ``PoC``. :func:`parse_findings_table`
extracts that table into a structured list for downstream comparison against
a ground-truth vulnerability list.
"""

import re
from typing import TypedDict


class ReportFinding(TypedDict):
    """A single row extracted from the final report's findings table."""

    endpoint: str
    vulnerability: str
    poc: str


_SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")


def _split_table_row(line: str) -> list[str] | None:
    """Split a markdown table row into stripped cells, or ``None`` if not a table row.

    Handles both ``| a | b |`` and ``a | b`` styles by dropping the empty
    cells produced by leading/trailing pipes.
    """
    stripped = line.strip()
    if "|" not in stripped:
        return None
    cells = [cell.strip() for cell in stripped.split("|")]
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells or None


def _is_separator_row(cells: list[str]) -> bool:
    """Return ``True`` if *cells* form a markdown table header separator row."""
    return all(_SEPARATOR_CELL_RE.match(cell) for cell in cells)


def parse_findings_table(report: str) -> list[ReportFinding]:
    """Extract endpoint/vulnerability/PoC rows from the report's findings table.

    Locates the first markdown table whose header row contains both an
    "endpoint" and a "vulnerability" column (case-insensitive, in any order),
    then parses the following rows into :class:`ReportFinding` dicts using
    those column positions plus a "poc" column if present. Missing columns or
    short rows yield empty strings. Returns an empty list if no matching table
    is found.
    """
    lines = report.splitlines()

    columns: dict[str, int] | None = None
    header_idx = -1
    for i, line in enumerate(lines):
        cells = _split_table_row(line)
        if cells is None:
            continue
        lowered = [cell.lower() for cell in cells]
        if "endpoint" in lowered and "vulnerability" in lowered:
            columns = {name: idx for idx, name in enumerate(lowered)}
            header_idx = i
            break

    if columns is None:
        return []

    endpoint_idx = columns["endpoint"]
    vulnerability_idx = columns["vulnerability"]
    poc_idx = columns.get("poc")

    def cell(cells: list[str], idx: int | None) -> str:
        if idx is None or idx >= len(cells):
            return ""
        return cells[idx]

    findings: list[ReportFinding] = []
    for line in lines[header_idx + 1 :]:
        cells = _split_table_row(line)
        if cells is None:
            break
        if _is_separator_row(cells):
            continue
        findings.append(
            {
                "endpoint": cell(cells, endpoint_idx),
                "vulnerability": cell(cells, vulnerability_idx),
                "poc": cell(cells, poc_idx),
            }
        )

    return findings
