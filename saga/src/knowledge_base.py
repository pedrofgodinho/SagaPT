"""Shared knowledge base for SagaPT agents.

Stores security findings as individual files in a directory hierarchy.
Keys are relative file paths (e.g. ``"recon/initial_recon/tool_logs/get_login.md"``).
A single ``KnowledgeBase`` instance is created at graph-build time and shared
across all agents in a run.
"""

import logging
import re
from pathlib import Path


logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    """Convert *text* to a filesystem-safe slug (lowercase alphanumerics + underscores)."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:80]


class KnowledgeBase:
    """Filesystem-backed store for security findings.

    Keys are relative file paths; values are written as plain files under a
    configured root directory so the store is crash-safe and human-readable.
    Falls back to in-memory-only operation when no root is configured (useful
    in tests and one-off CLI invocations).
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._kb_root: Path | None = None

    def set_root(self, path: Path) -> None:
        """Configure the root directory and flush any pre-existing content.

        Creates the directory if it does not exist. Idempotent when called
        with the same path twice.
        """
        path.mkdir(parents=True, exist_ok=True)
        self._kb_root = path
        for key, value in self._store.items():
            self._write_file(key, value)

    def _safe_path(self, rel: str) -> Path:
        """Resolve *rel* within the KB root, raising ``ValueError`` on traversal."""
        assert self._kb_root is not None
        root = self._kb_root.resolve()
        if not rel or rel == ".":
            return root
        rel_path = Path(rel)
        if rel_path.is_absolute() or rel_path.drive or ".." in rel_path.parts:
            raise ValueError(f"Path traversal attempt: {rel!r}")
        return root / rel

    def _write_file(self, key: str, value: str) -> None:
        """Write *value* to ``{kb_root}/{key}``, creating parent dirs as needed."""
        path = self._safe_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def store(self, key: str, value: str) -> None:
        """Store a finding at *key*. Overwrites any existing entry."""
        if key in self._store:
            logger.info("KB: overwriting existing key '%s'.", key)
        self._store[key] = value
        logger.debug("KB: stored key '%s'.", key)
        if self._kb_root is not None:
            self._write_file(key, value)

    def get(self, key: str) -> str | None:
        """Return the value for *key*, or ``None`` if not found."""
        return self._store.get(key)

    def list_keys(self) -> list[str]:
        """Return all stored paths in insertion order."""
        return list(self._store.keys())

    def list_dir(self, rel_path: str = "") -> list[str]:
        """List entry names directly under *rel_path* (not recursive).

        Returns file names and immediate subdirectory names, sorted
        alphabetically. An empty string or ``"."`` lists the KB root.
        Falls back to deriving the listing from in-memory keys when no root
        directory is configured.
        """
        if self._kb_root is not None:
            target = self._safe_path(rel_path)
            if not target.is_dir():
                return []
            return sorted(entry.name for entry in target.iterdir())
        # In-memory fallback: infer directory entries from stored key paths.
        prefix = (rel_path.rstrip("/") + "/") if rel_path and rel_path != "." else ""
        seen: set[str] = set()
        for key in self._store:
            if prefix and not key.startswith(prefix):
                continue
            remainder = key[len(prefix):]
            seen.add(remainder.split("/")[0])
        return sorted(seen)
