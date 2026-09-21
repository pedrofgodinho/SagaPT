**Vulnerability Class:** Reflected Cross-Site Scripting (XSS) — NOT PRESENT

**Endpoint:** POST `/login`

**Parameters Tested:** `username`, `password`

**Detection Payloads:**
- `<script>alert(1)</script>` in both `username` and `password` fields
- `XSS_LOGIN_TEST_PAYLOAD_789` in `username` field
- `XSS_PASS_TEST_PAYLOAD_456` in `password` field

**Evidence:**
- All POST requests to `/login` returned HTTP 200 with the authenticated homepage as response body
- None of the unique test payloads appeared anywhere in the response body, confirming the input fields are not reflected unescaped
- No ZAP XSS alerts were triggered for any of the login POST requests
- The `<script>alert(1)</script>` visible in the response body originates from a stored post (post ID 20), not from the login form

**Conclusion:** No reflected XSS vulnerability detected on the POST `/login` endpoint for the `username` or `password` parameters.