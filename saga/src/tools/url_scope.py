"""Code-level enforcement of the ``[zap] include``/``exclude`` scope patterns.

``saga.toml``'s ``include``/``exclude`` patterns are handed to ZAP's own
context API (``zap.context.include_in_context``/``exclude_from_context``),
which parses them as **Java/PCRE regex** (ZAP is a Java application) — notably
supporting ``\\Q...\\E`` literal-quoting, e.g. ``\\Qhttp://example.com\\E.*``.
That syntax is not valid in Python's ``re`` module (``\\Q`` raises
``re.error: bad escape``), so these patterns cannot be fed to ``re.compile``
as-is. This module reinterprets them for a Python-side allowlist check applied
before every outbound request in ``tools/zap_tools.py``, so a tool call can
never reach a host outside the run's configured scope — previously the
include/exclude patterns only ever scoped ZAP's own spider/context behaviour,
never the ad-hoc ``http_get``/``http_post``/etc. calls.
"""

import logging
import re
from collections.abc import Callable

logger = logging.getLogger(__name__)

_QE_PATTERN = re.compile(r"^\\Q(.*)\\E(.*)$", re.DOTALL)


def _pattern_to_matcher(pattern: str) -> Callable[[str], bool]:
    """Convert one ``saga.toml`` scope pattern into a Python URL predicate.

    Every pattern in the codebase today has the shape ``\\Q<literal>\\E`` or
    ``\\Q<literal>\\E.*`` (ZAP's literal-quote escape followed by an optional
    "anything after" wildcard) — translated here to a plain
    ``str.startswith(<literal>)`` check, which is exactly what that shape
    means. Anything else is tried as a plain Python regex, and if that also
    fails to compile, falls back to a literal-prefix check with a logged
    warning — a malformed config value should narrow/misbehave the scope
    check, never crash the run.
    """
    m = _QE_PATTERN.match(pattern)
    if m:
        literal, rest = m.groups()
        if rest == ".*":
            return lambda url: url.startswith(literal)
        if rest == "":
            return lambda url: url == literal

    try:
        compiled = re.compile(pattern)
    except re.error:
        logger.warning(
            "Scope pattern %r is not a valid Python regex; treating it as a "
            "literal URL prefix instead.",
            pattern,
        )
        return lambda url: url.startswith(pattern)
    return lambda url: compiled.match(url) is not None


def make_scope_checker(
    include: list[str] | None, exclude: list[str] | None
) -> Callable[[str], str | None]:
    """Build a ``url -> error message | None`` checker from scope patterns.

    Mirrors ZAP's own context semantics: an empty/absent ``include`` list
    means no restriction (matches today's default when a run supplies no
    ``[zap]`` config at all), while a non-empty ``include`` requires at least
    one pattern to match. ``exclude`` always wins over ``include``.
    """
    include_matchers = [_pattern_to_matcher(p) for p in (include or [])]
    exclude_matchers = [_pattern_to_matcher(p) for p in (exclude or [])]

    def check(url: str) -> str | None:
        if any(m(url) for m in exclude_matchers):
            return f"URL '{url}' is outside the allowed scope for this run (explicitly excluded)."
        if include_matchers and not any(m(url) for m in include_matchers):
            return f"URL '{url}' is outside the allowed scope for this run."
        return None

    return check
