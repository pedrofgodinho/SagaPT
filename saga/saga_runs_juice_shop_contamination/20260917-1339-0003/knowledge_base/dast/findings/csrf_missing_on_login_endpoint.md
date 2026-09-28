## Missing CSRF Protection on Login Endpoint

**Endpoint:** POST /rest/user/login
**Vulnerability Class:** Cross-Site Request Forgery (CSRF)

### Evidence
- The login endpoint accepts POST requests with JSON body (`application/json`) without requiring any CSRF token.
- No CSRF token was found in the static HTML page source (/, /#/login, /#/register).
- No `X-CSRF-Token` or similar anti-CSRF header was present in any response headers.
- Test: POST /rest/user/login with `{"email": "csrf@test.com", "password": "test"}` returned 401 without any CSRF token validation error.

### Test Performed
```
POST /rest/user/login
Content-Type: application/json
Body: {"email": "csrf@test.com", "password": "test"}
```
Response: HTTP 401 "Invalid email or password." (no CSRF error)

### Impact
An attacker could craft a malicious page that automatically submits a POST request to /rest/user/login on behalf of a logged-in user. Combined with the wide-open CORS (`Access-Control-Allow-Origin: *`), this could allow cross-origin CSRF attacks against authenticated users.

### Note
The login endpoint uses `application/json` content type. While browsers do not send cross-origin POST requests with arbitrary Content-Type via simple forms (preflight CORS is required for non-simple methods), the Angular SPA's JavaScript API calls could be exploited via cross-origin fetch/XHR if credentials are allowed.

### Remediation
Implement anti-CSRF tokens (e.g., double-submit cookie pattern) on all state-changing endpoints. Add `SameSite=Strict` or `SameSite=Lax` attribute to session cookies.