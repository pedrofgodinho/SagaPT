"""ZAP tool definitions for SagaPT agents.

All tools are created via ``make_zap_tools(zap_client, session, context_id)``
which returns a dict of tool name → ``BaseTool``.  Each tool is a closure bound
to the shared per-run ``ZapClient`` (proxy + ZAPv2 API), the shared
``requests.Session`` (for cookie persistence), and the active ZAP context ID.

Every run receives its own ``ZapClient`` — typically pointed at a per-run ZAP
container started by ``tools/zap_launcher.py`` — so no ZAP state is shared
across concurrent runs.

Available tools:

- ``http_get`` / ``http_post`` — passive scanning via ZAP proxy (all agents).
  Both accept a ``kb_key`` argument that the agent chooses; results are stored
  under that key in the knowledge base.  After each request the passive scan
  queue is drained and per-request ZAP alerts are fetched by message ID.
- ``spider`` — ZAP standard spider; crawls all links from a seed URL and
  returns discovered URLs plus aggregated passive-scan alerts.  Recon only.
- ``register_credentials`` — configure ZAP form-auth, create a ZAP user, and
  perform the initial login POST.  Stores credentials for reuse.  Recon only.
  Before each login POST, the login page is re-fetched and any hidden or
  submit ``<input>`` fields (a CSRF token like DVWA's ``user_token``,
  regenerated on every page load; or a submit button whose own field the
  server checks for, like DVWA's ``Login``) are merged into the POST data.
- ``login`` — re-authenticate using stored credentials.  DAST.  Also
  re-fetches and resends hidden/submit form fields, same as
  ``register_credentials``.
- ``logout`` — GET a logout URL and clear session cookies.  DAST.

Every tool that takes a caller-supplied URL checks it against the run's
``include``/``exclude`` scope (see ``tools/url_scope.py``) before making the
request, returning an ``error`` instead of firing an out-of-scope request.

Use ``setup_zap_context`` before ``make_zap_tools`` to create and configure the
ZAP context from ``saga.toml`` settings.
"""

import json
import logging
import os
import time
from html.parser import HTMLParser

import requests
import urllib3
from langchain_core.tools import BaseTool, tool
from zapv2 import ZAPv2

from tools.url_scope import make_scope_checker

logger = logging.getLogger(__name__)

# Process-wide tuning knobs — read once at import; not per-run.
_PASSIVE_SCAN_TIMEOUT = int(os.getenv("ZAP_PASSIVE_SCAN_TIMEOUT", "5"))
_SPIDER_TIMEOUT = int(os.getenv("ZAP_SPIDER_TIMEOUT", "120"))

# Suppress InsecureRequestWarning for proxied HTTPS traffic.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Alert fields useful to an LLM; description/solution are omitted (too verbose).
_ALERT_KEEP_FIELDS = frozenset({
    "risk", "confidence", "name", "url", "method",
    "param", "attack", "evidence", "pluginId",
})


class ZapClient:
    """Per-run handle to a single ZAP daemon.

    Bundles the ZAP daemon URL, its API key, the ``requests``-style proxy
    dict used to route traffic through it, and a lazily-constructed
    ``ZAPv2`` API client.  Every run owns its own ``ZapClient``, typically
    pointing at a run-scoped ZAP container spawned by
    ``tools/zap_launcher.py``; module-globals were removed so N concurrent
    runs never share ZAP state.
    """

    def __init__(self, url: str, api_key: str = "") -> None:
        self.url = url
        self.api_key = api_key
        self.proxies: dict[str, str] = {"http": url, "https": url}
        self.zap = ZAPv2(apikey=api_key, proxies=self.proxies)


def _wait_for_passive_scan(zap: ZAPv2, timeout_secs: int = _PASSIVE_SCAN_TIMEOUT) -> None:
    """Poll the ZAP passive scan queue until it drains or the timeout expires."""
    deadline = time.monotonic() + timeout_secs
    while time.monotonic() < deadline:
        remaining = int(zap.pscan.records_to_scan)
        if remaining == 0:
            break
        time.sleep(0.5)
    logger.debug("Passive scan queue drained (or timeout reached).")


def _get_alerts_for_message(zap: ZAPv2, url: str, msg_id: str) -> list[dict]:
    """Return de-duplicated, trimmed ZAP alerts for a specific message ID.

    Filters ``zap.core.alerts(baseurl=url)`` to only those whose ``messageId``
    matches *msg_id*, deduplicates by ``(pluginId, evidence)``, strips noisy
    fields, and caps results at 20.
    """
    raw_alerts: list[dict] = zap.core.alerts(baseurl=url) or []
    filtered = [a for a in raw_alerts if str(a.get("messageId", "")) == str(msg_id)]

    seen: set[tuple[str, str]] = set()
    unique: list[dict] = []
    for a in filtered:
        key = (str(a.get("pluginId", "")), str(a.get("evidence", "")))
        if key not in seen:
            seen.add(key)
            unique.append({k: v for k, v in a.items() if k in _ALERT_KEEP_FIELDS})

    return unique[:20]


class _HiddenInputParser(HTMLParser):
    """Collects name/value pairs of ``<input type="hidden">`` and ``type="submit"`` elements.

    Hidden fields catch CSRF tokens; the submit field catches forms whose
    server-side handler only runs its login logic when that specific
    name/value pair is present in the POST body (e.g. DVWA's ``login.php``
    checks ``isset($_POST['Login'])`` before doing anything else — a login
    POST that's missing the submit button's own field is silently ignored
    and just redisplays the login form, with no error).
    """

    def __init__(self) -> None:
        super().__init__()
        self.fields: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "input":
            return
        attr_map = dict(attrs)
        if (attr_map.get("type") or "").lower() not in ("hidden", "submit"):
            return
        name = attr_map.get("name")
        if name:
            self.fields[name] = attr_map.get("value") or ""


def _parse_hidden_fields(html: str) -> dict[str, str]:
    """Extract name/value pairs of every hidden and submit ``<input>`` in *html*.

    Used to pick up CSRF tokens (e.g. DVWA's ``user_token``) that must be
    resent alongside login credentials but are regenerated on every page
    load, and submit-button fields that some server-side handlers require
    to be present to recognize the form was actually submitted.
    """
    parser = _HiddenInputParser()
    parser.feed(html)
    return parser.fields


def _fetch_hidden_fields(session: requests.Session, login_url: str) -> dict[str, str]:
    """GET *login_url* and return its hidden/submit form field name/value pairs.

    Returns an empty dict (rather than raising) on any request failure —
    most targets have no such fields at all, so a failed pre-fetch
    shouldn't block the login attempt itself.
    """
    try:
        response = session.get(login_url, timeout=30)
    except requests.RequestException as exc:
        logger.warning(
            "Could not pre-fetch login page '%s' for hidden fields: %s", login_url, exc
        )
        return {}
    return _parse_hidden_fields(response.text)


def setup_zap_context(
    zap_client: ZapClient,
    context_name: str,
    include: list[str],
    exclude: list[str],
) -> int:
    """Create a named ZAP context and configure include/exclude URL patterns.

    Should be called once per run before ``make_zap_tools``.  The returned
    ``context_id`` is passed to ``make_zap_tools`` so tools can reference it
    (e.g. for future authenticated scanning).

    Args:
        zap_client: The run's ``ZapClient`` handle.
        context_name: Display name for the context in ZAP.
        include: List of regex patterns for URLs in scope.
        exclude: List of regex patterns for URLs to exclude.

    Returns:
        The integer context ID assigned by ZAP.
    """
    zap = zap_client.zap
    result = zap.context.new_context(context_name)
    if result == "already_exists":
        context_id = int(zap.context.context(context_name)["id"])
        logger.info(
            "ZAP context '%s' already exists (id=%d), reusing.",
            context_name,
            context_id,
        )
        return context_id
    context_id = int(result)
    for pattern in include:
        zap.context.include_in_context(context_name, pattern)
    for pattern in exclude:
        zap.context.exclude_from_context(context_name, pattern)
    logger.info(
        "ZAP context '%s' created (id=%d, %d include pattern(s), %d exclude pattern(s)).",
        context_name,
        context_id,
        len(include),
        len(exclude),
    )
    return context_id


def _read_body_tolerant(response: requests.Response) -> tuple[str, bool]:
    """Read a response body, tolerating a truncated or mis-framed transfer.

    Some targets send a ``Content-Length`` that overshoots the bytes actually
    delivered.  OWASP Juice Shop's ``/ftp/`` directory listing is a concrete
    example: it declares 11322 bytes but sends a complete, valid 11263-byte
    body, so the *uncompressed* transfer ends 59 bytes short of its own header
    (the compressed transfer is framed correctly, which is why the bug only
    surfaces through ZAP — ZAP requests identity encoding to inspect plaintext).
    ``requests``/``urllib3`` strictly enforce ``Content-Length`` and raise
    ``ChunkedEncodingError``/``ProtocolError`` when the stream ends early;
    uncaught, that exception propagates out of the tool and aborts the *entire*
    run over a single malformed response.  We instead keep whatever bytes did
    arrive — typically a complete, usable body — and report that the transfer
    was cut short.

    The response must have been issued with ``stream=True`` so its body was not
    already read eagerly inside ``Session.send`` (where the same error would be
    raised before we could catch it).

    Args:
        response: A streamed ``requests.Response`` whose body has not yet been
            consumed.

    Returns:
        ``(text, truncated)`` — the decoded body, and whether the underlying
        transfer was cut short before the declared length was reached.
    """
    raw = response.raw
    # urllib3 (v2) raises ``IncompleteRead`` the instant a transfer ends short of
    # its declared ``Content-Length`` — and discards the final, partially
    # buffered chunk along with it.  Disable that enforcement so we keep *every*
    # byte the target actually sent (the tail of a directory listing or JSON
    # array is often the interesting part); the short transfer is detected below
    # from ``length_remaining`` instead.
    try:
        raw.enforce_content_length = False
    except AttributeError:
        pass  # non-urllib3 transport (e.g. a test stub) — rely on the except path

    chunks: list[bytes] = []
    truncated = False
    try:
        for chunk in response.iter_content(chunk_size=8192):
            chunks.append(chunk)
    except (requests.exceptions.ChunkedEncodingError, urllib3.exceptions.ProtocolError) as exc:
        # Reached only if enforcement could not be disabled; keep what arrived.
        truncated = True
        logger.warning(
            "Truncated transfer for '%s': %s (keeping %d byte(s) received).",
            response.url,
            exc,
            sum(len(c) for c in chunks),
        )

    # A positive ``length_remaining`` means the stream reached its end still
    # short of the declared ``Content-Length`` — a mis-framed but recoverable
    # body (see Juice Shop's ``/ftp/``).
    remaining = getattr(raw, "length_remaining", None)
    if remaining:
        if not truncated:
            logger.warning(
                "Short transfer for '%s': %d byte(s) fewer than the declared "
                "Content-Length (kept the %d byte(s) delivered).",
                response.url,
                remaining,
                sum(len(c) for c in chunks),
            )
        truncated = True

    # Populate the response so its normal ``.text`` decoding (charset detection
    # included) applies to exactly the bytes we collected.
    response._content = b"".join(chunks)
    response._content_consumed = True
    return response.text, truncated


def make_zap_tools(
    zap_client: ZapClient,
    session: requests.Session,
    context_id: int | None = None,
    context_name: str | None = None,
    spider_exclude: list[str] | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> dict[str, BaseTool]:
    """Create ZAP tool closures bound to *zap_client*, *session*, and *context_id*.

    The session is configured to route all traffic through *zap_client*'s ZAP
    proxy so every request is passively scanned.  *context_id* and
    *context_name* are captured in each closure for use by
    authentication-aware and spider tools.

    Returns a dict keyed by tool name.  Any entries in ``TOOL_REGISTRY``
    (test fakes) are merged in so tests can inject tools without code changes.

    Args:
        zap_client: The run's ``ZapClient`` handle.  Every ZAP call inside
            the returned tools goes through this client — so N concurrent
            runs each holding their own ``ZapClient`` never share state.
        session: Shared ``requests.Session``; cookies are preserved across calls.
        context_id: ZAP context ID returned by ``setup_zap_context``, or
            ``None`` if context setup was skipped (e.g. in tests).
        context_name: ZAP context name matching *context_id*.  When provided,
            the spider tool scopes its scan to this context so that context-level
            include/exclude URL rules are respected.  ``None`` means no context
            scoping (spider crawls without restriction beyond its own exclusions).
        spider_exclude: Additional URL regex patterns passed to
            ``zap.spider.exclude_from_scan()`` before each spider run.  Use
            these for endpoints that must never be crawled (e.g. logout,
            delete, destructive admin actions), independently of the broader
            context exclusions.
        include: Same patterns passed to ``setup_zap_context`` (``saga.toml``'s
            ``[zap] include``).  Reused here to build a code-level allowlist
            (see ``tools/url_scope.py``) enforced on every request-issuing
            tool — empty/``None`` means unrestricted, matching ZAP's own
            context semantics.
        exclude: Same as *include*, for denied URLs; always takes precedence.
    """
    # Bind once — captured by every closure below.
    zap = zap_client.zap
    # Route all session traffic through this run's ZAP.
    session.proxies = zap_client.proxies
    session.verify = False  # type: ignore[assignment]

    check_scope = make_scope_checker(include, exclude)

    # Credentials stored by register_credentials for use by login/logout.
    _auth_state: dict[str, str] = {}

    @tool
    def http_get(url: str, kb_key: str) -> dict:
        """Send an HTTP GET request through the ZAP proxy.

        Routes the request through ZAP for passive scanning. After the request,
        waits for the passive scan queue to drain, then retrieves any ZAP alerts
        raised specifically for this request (correlated by ZAP message ID).

        Returns a dict with the response status code, headers, the full response
        body, a list of ZAP alerts for this request, and the kb_key. A large body
        is shortened in the tool result shown to you, but the full untruncated
        body is stored in the knowledge base under the raw-output key reported in
        the result; fetch it with kb_get when you need more than what is shown.
        The kb_key you provide will be used to store results in the knowledge base.

        Args:
            url: The URL to request.
            kb_key: A short, descriptive key under which this result will be stored
                in the knowledge base (e.g. "login page unauthenticated").
                Choose a unique key for each distinct request so results do not
                overwrite each other.
        """
        scope_error = check_scope(url)
        if scope_error is not None:
            logger.warning("http_get blocked: %s", scope_error)
            return {"error": scope_error, "kb_key": kb_key}

        msgs_before: list[dict] = zap.core.messages(baseurl=url) or []
        n_before = len(msgs_before)

        logger.info("HTTP GET '%s' via ZAP proxy (kb_key=%r).", url, kb_key)
        try:
            response = session.get(url, timeout=30, stream=True)
            body, body_truncated = _read_body_tolerant(response)
        except requests.RequestException as exc:
            logger.warning("HTTP GET '%s' failed: %s", url, exc)
            return {"error": f"Request failed: {exc}", "kb_key": kb_key}
        logger.debug(
            "HTTP GET '%s' → %d (%d byte(s)%s).",
            url,
            response.status_code,
            len(body),
            ", transfer truncated" if body_truncated else "",
        )

        _wait_for_passive_scan(zap)

        msgs_after: list[dict] = zap.core.messages(baseurl=url) or []
        new_msgs = msgs_after[n_before:]
        alerts: list[dict] = []
        if new_msgs:
            our_msg_id = str(new_msgs[-1].get("id", ""))
            alerts = _get_alerts_for_message(zap, url, our_msg_id)
            logger.debug("HTTP GET '%s': %d alert(s) for message id=%s.", url, len(alerts), our_msg_id)

        result = {
            "status": response.status_code,
            "headers": dict(response.headers),
            "body": body,
            "alerts": alerts,
            "kb_key": kb_key,
        }
        if body_truncated:
            result["body_truncated"] = True
        return result

    @tool
    def http_post(url: str, data: str, kb_key: str, content_type: str = "json") -> dict:
        """Send an HTTP POST request through the ZAP proxy.

        ``data`` must always be a valid JSON string (a flat object of field
        names to values), but how it is transmitted depends on ``content_type``:

        - ``"json"`` (default): sent as the request body with
          ``Content-Type: application/json``. Use this for JSON APIs.
        - ``"form"``: sent as ``application/x-www-form-urlencoded``, the way a
          browser submits an HTML ``<form>``. Use this for standard web forms —
          logins, signups, and most non-API endpoints. If a JSON POST gets
          rejected with a 400 before your payload seems to reach the
          application logic, retry with ``content_type="form"``.

        Routes through ZAP for passive scanning. After the request, waits for
        the passive scan queue to drain, then retrieves any ZAP alerts raised
        specifically for this request (correlated by ZAP message ID).

        Returns a dict with the response status code, headers, the full response
        body, a list of ZAP alerts for this request, and the kb_key. A large body
        is shortened in the tool result shown to you, but the full untruncated
        body is stored in the knowledge base under the raw-output key reported in
        the result; fetch it with kb_get when you need more than what is shown.

        Args:
            url: The URL to POST to.
            data: A valid JSON string (flat object) to send as the request body.
            kb_key: A short, descriptive key under which this result will be stored
                in the knowledge base (e.g. "login attempt admin").
                Choose a unique key for each distinct request.
            content_type: ``"json"`` or ``"form"``. See above.
        """
        if content_type not in ("json", "form"):
            return {"error": f"Invalid content_type: {content_type!r}. Must be 'json' or 'form'."}

        scope_error = check_scope(url)
        if scope_error is not None:
            logger.warning("http_post blocked: %s", scope_error)
            return {"error": scope_error, "kb_key": kb_key}

        msgs_before: list[dict] = zap.core.messages(baseurl=url) or []
        n_before = len(msgs_before)

        logger.info(
            "HTTP POST '%s' via ZAP proxy (kb_key=%r, content_type=%r).", url, kb_key, content_type
        )
        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            return {"error": f"Invalid JSON data: {exc}"}
        try:
            if content_type == "form":
                response = session.post(url, data=payload, timeout=30, stream=True)
            else:
                response = session.post(url, json=payload, timeout=30, stream=True)
            body, body_truncated = _read_body_tolerant(response)
        except requests.RequestException as exc:
            logger.warning("HTTP POST '%s' failed: %s", url, exc)
            return {"error": f"Request failed: {exc}", "kb_key": kb_key}
        logger.debug(
            "HTTP POST '%s' → %d (%d byte(s)%s).",
            url,
            response.status_code,
            len(body),
            ", transfer truncated" if body_truncated else "",
        )

        _wait_for_passive_scan(zap)

        msgs_after: list[dict] = zap.core.messages(baseurl=url) or []
        new_msgs = msgs_after[n_before:]
        alerts: list[dict] = []
        if new_msgs:
            our_msg_id = str(new_msgs[-1].get("id", ""))
            alerts = _get_alerts_for_message(zap, url, our_msg_id)
            logger.debug("HTTP POST '%s': %d alert(s) for message id=%s.", url, len(alerts), our_msg_id)

        result = {
            "status": response.status_code,
            "headers": dict(response.headers),
            "body": body,
            "alerts": alerts,
            "kb_key": kb_key,
        }
        if body_truncated:
            result["body_truncated"] = True
        return result

    @tool
    def register_credentials(
        login_url: str,
        username: str,
        password: str,
        kb_key: str,
        username_field: str = "username",
        password_field: str = "password",
        logged_in_indicator: str = "",
        logged_out_indicator: str = "",
    ) -> dict:
        """Configure form-based authentication on the active ZAP context and perform the initial login.

        Sets up a form-based login flow for the context, creates a ZAP user
        with the given credentials, enables that user, and activates forced
        user mode so that all subsequent requests through the ZAP proxy are
        automatically authenticated as this user.  Also stores the credentials
        in memory so that ``login`` can re-authenticate without parameters.

        Make sure to set the logged in indicator and/or logged out indicator.
        Look for strings that only appear in the page when logged in, or
        only appear when logged out. For example, look for "Log in" or
        "Sign in" for the logged out indicator, or "Log out" or "Sign out"
        for the logged in indicator. You can call this tool multiple times to
        update the indicators, if you couldn't find good ones before login.

        Args:
            login_url: Full URL of the login endpoint (e.g.
                ``http://example.com/login``).
            username: Username credential.
            password: Password credential.
            kb_key: A short, descriptive key under which this result will be stored
                in the knowledge base (e.g. "register credentials mr_robot").
            username_field: Name of the HTML username field (default
                ``"username"``).
            password_field: Name of the HTML password field (default
                ``"password"``).
            logged_in_indicator: Regex pattern matched against response body to
                detect a successful login (e.g. ``"\\\\QWelcome\\\\E"``). Leave
                empty to skip.
            logged_out_indicator: Regex pattern matched against response body to
                detect a logged-out state (e.g. ``"\\\\QSign in\\\\E"``). Leave
                empty to skip.

        Returns:
            JSON with ``user_id`` on success, or ``error`` on failure.
        """
        if context_id is None:
            return {"error": "No ZAP context available — context setup was skipped.", "kb_key": kb_key}

        scope_error = check_scope(login_url)
        if scope_error is not None:
            logger.warning("register_credentials blocked: %s", scope_error)
            return {"error": scope_error, "kb_key": kb_key}

        logger.info(
            "Configuring form-based auth on context %d: login_url='%s', user='%s'.",
            context_id,
            login_url,
            username,
        )

        from urllib.parse import quote

        login_request_data = (
            f"{quote(username_field)}=%7B%25username%25%7D"
            f"%26{quote(password_field)}=%7B%25password%25%7D"
        )
        auth_config = f"loginUrl={quote(login_url, safe=':/')}&loginRequestData={login_request_data}"
        zap.authentication.set_authentication_method(
            context_id,
            "formBasedAuthentication",
            auth_config,
        )
        logger.debug("Auth method set on context %d.", context_id)

        if logged_in_indicator:
            zap.authentication.set_logged_in_indicator(context_id, logged_in_indicator)
            logger.debug("Logged-in indicator set: '%s'.", logged_in_indicator)
        if logged_out_indicator:
            zap.authentication.set_logged_out_indicator(
                context_id, logged_out_indicator
            )
            logger.debug("Logged-out indicator set: '%s'.", logged_out_indicator)

        user_id = zap.users.new_user(context_id, username)
        credentials = f"username={quote(username)}&password={quote(password)}"
        zap.users.set_authentication_credentials(context_id, user_id, credentials)
        zap.users.set_user_enabled(context_id, user_id, "true")
        logger.info(
            "ZAP user '%s' created (user_id=%s) on context %d.",
            username,
            user_id,
            context_id,
        )

        zap.forcedUser.set_forced_user(context_id, user_id)
        zap.forcedUser.set_forced_user_mode_enabled("true")
        logger.info(
            "Forced user mode enabled for user_id=%s on context %d.",
            user_id,
            context_id,
        )

        # Perform the actual login through the session so it acquires auth
        # cookies.  ZAP's forced-user mode only applies when ZAP itself is the
        # request initiator (spider/active scan); pass-through requests from an
        # external requests.Session are not automatically authenticated by ZAP.
        # Some targets (e.g. DVWA) embed a per-page-load CSRF token as a hidden
        # form field, and/or gate their login logic on the submit button's own
        # field being present in the POST body — so the login page is fetched
        # fresh and its hidden/submit fields merged in alongside credentials.
        hidden_fields = _fetch_hidden_fields(session, login_url)
        login_response = session.post(
            login_url,
            data={**hidden_fields, username_field: username, password_field: password},
            timeout=30,
            allow_redirects=True,
        )
        logger.info(
            "Login POST to '%s' → %d; session now has %d cookie(s).",
            login_url,
            login_response.status_code,
            len(session.cookies),
        )

        # Store credentials for later use by login() and spider().
        _auth_state["login_url"] = login_url
        _auth_state["username"] = username
        _auth_state["password"] = password
        _auth_state["username_field"] = username_field
        _auth_state["password_field"] = password_field
        _auth_state["user_id"] = user_id

        return {
            "user_id": user_id,
            "context_id": context_id,
            "kb_key": kb_key,
        }

    @tool
    def login(kb_key: str) -> str:
        """Log in using the credentials registered by ``register_credentials``.

        Re-authenticates the shared HTTP session by POSTing to the remembered
        login URL with the stored credentials.  Use this to restore an
        authenticated session after calling ``logout``, or at the start of a
        task that requires authentication.

        ``register_credentials`` must have been called in a prior step;
        returns an error if no credentials are stored.

        Args:
            kb_key: A short, descriptive key under which this result will be stored
                in the knowledge base (e.g. "login as mr_robot").

        Returns:
            A dict with ``status`` (HTTP response code) and ``cookies`` (count)
            on success, or ``error`` on failure.
        """
        if not _auth_state.get("login_url"):
            return {"error": "No credentials registered — call register_credentials first.", "kb_key": kb_key}
        login_url = _auth_state["login_url"]
        scope_error = check_scope(login_url)
        if scope_error is not None:
            logger.warning("login blocked: %s", scope_error)
            return {"error": scope_error, "kb_key": kb_key}
        username_field = _auth_state["username_field"]
        password_field = _auth_state["password_field"]
        logger.info("Login POST to '%s' using stored credentials.", login_url)
        hidden_fields = _fetch_hidden_fields(session, login_url)
        response = session.post(
            login_url,
            data={
                **hidden_fields,
                username_field: _auth_state["username"],
                password_field: _auth_state["password"],
            },
            timeout=30,
            allow_redirects=True,
        )
        logger.info(
            "Login POST → %d; session now has %d cookie(s).",
            response.status_code,
            len(session.cookies),
        )
        return {
            "status": response.status_code,
            "cookies": len(session.cookies),
            "kb_key": kb_key,
        }

    @tool
    def logout(logout_url: str, kb_key: str) -> dict:
        """Log out by visiting the logout URL and clearing session cookies.

        Sends a GET request to *logout_url* through the ZAP proxy (for passive
        scanning), then clears all cookies from the shared session so that
        subsequent requests are unauthenticated.  Use this to test
        unauthenticated flows or access-control boundaries.

        Args:
            logout_url: Full URL of the logout endpoint (e.g.
                ``http://example.com/logout``).
            kb_key: A short, descriptive key under which this result will be stored
                in the knowledge base (e.g. "logout mr_robot").

        Returns:
            A dict with ``status`` (HTTP response code) on success, or ``error``
            on failure.
        """
        scope_error = check_scope(logout_url)
        if scope_error is not None:
            logger.warning("logout blocked: %s", scope_error)
            return {"error": scope_error, "kb_key": kb_key}

        logger.info("Logout GET '%s'; will clear session cookies after.", logout_url)
        response = session.get(logout_url, timeout=30, allow_redirects=True)
        session.cookies.clear()
        logger.info(
            "Logout GET → %d; session cookies cleared.",
            response.status_code,
        )
        return {
            "status": response.status_code,
            "message": "Session cookies cleared.",
            "kb_key": kb_key,
        }

    @tool
    def spider(url: str, kb_key: str, max_depth: int = 5) -> dict:
        """Crawl a URL using the ZAP standard spider.

        Starts a ZAP spider scan rooted at *url*, polls until it completes or
        ``ZAP_SPIDER_TIMEOUT`` seconds elapse, then waits for the passive scan
        queue to drain and collects any ZAP alerts raised during the crawl.

        Use this at the start of reconnaissance to discover all reachable URLs
        before probing individual endpoints with ``http_get`` or ``http_post``.

        Spider-specific URL exclusions configured in ``saga.toml`` under
        ``[zap] spider_exclude`` are applied automatically before the scan
        starts; you do not need to filter the results yourself.

        Args:
            url: Seed URL to start crawling from (e.g. ``http://target:5000``).
            kb_key: Short descriptive label for KB storage
                (e.g. ``"spider homepage"``). Must be unique per invocation.
            max_depth: Maximum crawl depth (default 5).

        Returns:
            A dict with ``discovered_urls`` (list, capped at 500),
            ``url_count`` (int), ``alerts`` (list, capped at 50), and
            ``kb_key``.
        """
        scope_error = check_scope(url)
        if scope_error is not None:
            logger.warning("spider blocked: %s", scope_error)
            return {"error": scope_error, "kb_key": kb_key}

        logger.info(
            "Spider scan starting at '%s' (kb_key=%r, max_depth=%d).",
            url,
            kb_key,
            max_depth,
        )

        # Apply spider-specific exclusions before starting the scan.
        for pattern in (spider_exclude or []):
            zap.spider.exclude_from_scan(pattern)
            logger.debug("Spider: excluded pattern '%s'.", pattern)

        uid = _auth_state.get("user_id")
        if context_id is not None and uid is not None:
            # Authenticated spider: ZAP logs in as the registered user before
            # crawling so that pages behind authentication are reachable.
            scan_id = zap.spider.scan_as_user(context_id, uid, url, maxchildren=0, recurse=True)
        else:
            scan_id = zap.spider.scan(
                url=url,
                maxchildren=0,
                recurse=True,
                contextname=context_name,  # None → ZAP ignores it (no context scoping)
            )

        # ZAP returns an error string (e.g. "url_not_in_context") instead of a
        # numeric ID when the seed URL is outside the active context scope.
        try:
            scan_id = int(scan_id)
        except (ValueError, TypeError):
            logger.error(
                "Spider rejected by ZAP (scan_id=%r). "
                "Likely cause: URL '%s' is not within the context scope "
                "(check saga.toml [zap] include patterns). Falling back to core.urls().",
                scan_id,
                url,
            )
            results = zap.core.urls(baseurl=url) or []
            logger.info("Spider '%s': %d URL(s) from core.urls() fallback.", url, len(results))
            print(f"  [spider] error — scan rejected by ZAP (scan_id={scan_id!r})", flush=True)
            return {
                "discovered_urls": results[:500],
                "url_count": len(results),
                "alerts": [],
                "kb_key": kb_key,
                "error": f"Spider rejected by ZAP: scan_id={scan_id!r}. URL may be out of context scope.",
            }

        logger.debug("Spider scan_id=%d started.", scan_id)

        # Poll until complete or timeout, logging progress every 10 seconds.
        deadline = time.monotonic() + _SPIDER_TIMEOUT
        last_logged_progress = -1
        last_log_time = time.monotonic() - 10  # ensure first iteration always logs
        while time.monotonic() < deadline:
            try:
                progress = int(zap.spider.status(scan_id))
            except (ValueError, TypeError):
                progress = 0
            now = time.monotonic()
            if progress != last_logged_progress and (now - last_log_time >= 10 or progress >= 100):
                print(f"  [spider] {progress}% complete", flush=True)
                last_logged_progress = progress
                last_log_time = now
            if progress >= 100:
                break
            time.sleep(2)
        else:
            logger.warning("Spider scan timed out after %ds; stopping.", _SPIDER_TIMEOUT)
            print(f"  [spider] timed out after {_SPIDER_TIMEOUT}s", flush=True)
            zap.spider.stop(scan_id)

        # zap.spider.results() can return a plain string (e.g. "does_not_exist")
        # on some ZAP versions.  Fall back to zap.core.urls() which is always
        # reliable for in-scope URL discovery.
        raw_results = zap.spider.results(scan_id)
        if isinstance(raw_results, list):
            results: list[str] = raw_results
        else:
            logger.debug("spider.results returned %r; falling back to core.urls.", raw_results)
            results = zap.core.urls(baseurl=url) or []
        logger.info("Spider '%s': %d URL(s) discovered.", url, len(results))
        print(f"  [spider] done — {len(results)} URL(s) discovered", flush=True)

        _wait_for_passive_scan(zap)

        # Aggregate de-duplicated alerts for the base URL.
        raw_alerts: list[dict] = zap.core.alerts(baseurl=url) or []
        seen: set[tuple[str, str]] = set()
        alerts: list[dict] = []
        for a in raw_alerts:
            key = (str(a.get("pluginId", "")), str(a.get("evidence", "")))
            if key not in seen:
                seen.add(key)
                alerts.append({k: v for k, v in a.items() if k in _ALERT_KEEP_FIELDS})
        alerts = alerts[:50]

        return {
            "discovered_urls": results[:500],
            "url_count": len(results),
            "alerts": alerts,
            "kb_key": kb_key,
        }

    tool_map: dict[str, BaseTool] = {
        "http_get": http_get,
        "http_post": http_post,
        "register_credentials": register_credentials,
        "login": login,
        "logout": logout,
        "spider": spider,
    }
    # Merge in any test fakes from TOOL_REGISTRY.
    for name, t in TOOL_REGISTRY.items():
        if name not in tool_map:
            tool_map[name] = t
    return tool_map


# Mutable registry used exclusively as an injection point for test fakes.
# Register a fake tool here before calling make_zap_tools() and it will appear
# in the returned tool map.  Never populate this in production code.
TOOL_REGISTRY: dict[str, BaseTool] = {}
