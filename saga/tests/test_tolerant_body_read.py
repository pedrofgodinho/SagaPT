"""Unit tests for ``tools.zap_tools._read_body_tolerant``.

A target can advertise a ``Content-Length`` that overshoots the bytes it
actually delivers.  OWASP Juice Shop's ``/ftp/`` directory listing is the
motivating case: it declares 11322 bytes but sends a complete, valid 11263-byte
body, so the uncompressed transfer ends 59 bytes short of its own header.
``requests``/``urllib3`` enforce ``Content-Length`` and raise
``ChunkedEncodingError``; uncaught, that single malformed response aborts the
whole run.

``_read_body_tolerant`` disables urllib3's length enforcement so every
delivered byte is kept (the tail of a listing is often the interesting part),
detects the short transfer from ``length_remaining``, and — as a fallback for
transports where enforcement can't be disabled — still recovers gracefully if
the read does raise.  These tests exercise both paths with a fake raw stream, so
no ZAP or live target is required.
"""

import requests
from urllib3.exceptions import IncompleteRead, ProtocolError

from tools.zap_tools import _read_body_tolerant


class _FakeRaw:
    """Stand-in for a urllib3 raw response stream.

    Mirrors the two attributes ``_read_body_tolerant`` relies on:

    - ``enforce_content_length`` — when the helper sets this ``False`` the
      stream yields all chunks without raising, exactly like urllib3.
    - ``length_remaining`` — bytes still owed against ``Content-Length`` once the
      stream is exhausted; ``> 0`` signals a short transfer.

    ``requests.iter_content`` calls ``raw.stream(chunk_size, decode_content=)``
    and converts a ``ProtocolError`` into ``ChunkedEncodingError``.
    """

    def __init__(
        self,
        chunks: list[bytes],
        *,
        length_remaining: int = 0,
        raise_even_when_unenforced: bool = False,
    ) -> None:
        self._chunks = chunks
        self.enforce_content_length = True
        self.length_remaining = length_remaining
        self._raise_even_when_unenforced = raise_even_when_unenforced

    def stream(self, amt: int = 8192, decode_content: bool = True):
        yield from self._chunks
        # urllib3 raises only while enforcement is on — unless we're simulating a
        # transport whose framing error can't be silenced (the fallback path).
        if self._raise_even_when_unenforced or self.enforce_content_length:
            if self.length_remaining:
                raise ProtocolError(
                    "Connection broken: IncompleteRead("
                    f"{sum(len(c) for c in self._chunks)} bytes read, "
                    f"{self.length_remaining} more expected)",
                    IncompleteRead(sum(len(c) for c in self._chunks), self.length_remaining),
                )


def _make_response(raw: _FakeRaw) -> requests.Response:
    resp = requests.Response()
    resp.raw = raw
    resp.status_code = 200
    resp.encoding = "utf-8"
    resp.url = "http://juiceshop.local:3000/ftp/"
    return resp


def test_short_transfer_keeps_full_body_via_length_remaining():
    """The production path: enforcement is disabled, so the whole body is kept
    and truncation is detected from ``length_remaining``."""
    raw = _FakeRaw([b"<html>", b"...complete body...", b"</html>"], length_remaining=59)

    text, truncated = _read_body_tolerant(_make_response(raw))

    assert truncated is True
    assert text == "<html>...complete body...</html>"  # nothing lost, incl. the tail


def test_clean_transfer_reads_full_body_and_flags_false():
    """A well-framed transfer reads normally and reports no truncation."""
    raw = _FakeRaw([b"hello ", b"world"], length_remaining=0)

    text, truncated = _read_body_tolerant(_make_response(raw))

    assert truncated is False
    assert text == "hello world"


def test_hard_framing_error_still_recovers_partial_body():
    """Fallback path: a transport that raises even with enforcement off must not
    crash the run — keep the bytes that arrived and flag the truncation."""
    raw = _FakeRaw(
        [b"partial-", b"content"],
        length_remaining=59,
        raise_even_when_unenforced=True,
    )

    text, truncated = _read_body_tolerant(_make_response(raw))

    assert truncated is True
    assert text == "partial-content"


def test_utf8_body_is_decoded_with_the_response_encoding():
    """Multibyte content is decoded via the response encoding, not byte-sliced."""
    raw = _FakeRaw(["café ".encode("utf-8"), "☕".encode("utf-8")], length_remaining=12)

    text, truncated = _read_body_tolerant(_make_response(raw))

    assert truncated is True
    assert text == "café ☕"


def test_raw_that_rejects_enforcement_toggle_is_tolerated():
    """A raw object that can't accept ``enforce_content_length = False`` (here a
    ``__slots__`` stub) must be handled without an ``AttributeError`` escaping."""

    class _SlottedRaw:
        __slots__ = ()

        def stream(self, amt: int = 8192, decode_content: bool = True):
            yield b"body"

    resp = requests.Response()
    resp.raw = _SlottedRaw()
    resp.status_code = 200
    resp.encoding = "utf-8"
    resp.url = "http://x/"

    text, truncated = _read_body_tolerant(resp)
    assert text == "body"
    assert truncated is False
