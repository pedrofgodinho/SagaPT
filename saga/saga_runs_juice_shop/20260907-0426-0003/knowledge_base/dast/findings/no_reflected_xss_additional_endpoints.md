# No Reflected XSS in Additional Endpoints

- **Vulnerability Class**: Reflected Cross-Site Scripting (XSS) - NOT PRESENT
- **Endpoints Tested**:
  1. `GET /api/SecurityQuestions` - Static data endpoint
  2. `GET /nonexistent` - SPA fallback page
  3. `GET /api/nonexistent` - 500 error page with path reflection
  4. `GET /api/Feedbacks` - Stored feedbacks listing
  5. `GET /api/Users/{id}` - User data (requires auth)

- **Payloads Tested**:
  - `<script>alert(1)</script>`
  - `<svg/onload=alert(1)>`
  - `"><script>alert(1)</script>`
  - `<img src=x onerror=alert(1)>`
  - URL-encoded variants of all payloads

- **Results**:

  1. **`/api/SecurityQuestions`**: Returns static JSON with 14 hardcoded security questions. No user input is reflected. No XSS.

  2. **`/nonexistent`**: Returns the main SPA HTML (status 200) with `<app-root></app-root>` as the only dynamic element. The URL path is NOT reflected in the response body. No XSS.

  3. **`/api/nonexistent`**: Returns 500 error page. The URL path IS reflected in the HTML `<h2>` tag, e.g., `Error: Unexpected path: /api/<path>`. However, XSS payloads are **URL-encoded** in the response (e.g., `%3Cscript%3Ealert(1)%3C/script%3E` instead of `<script>alert(1)</script>`). URL-encoded entities are NOT interpreted as HTML by browsers — they render as literal text. **Not a confirmed XSS vulnerability.**

  4. **`/api/Feedbacks`**: Returns pre-populated feedback data as JSON. Some comments contain HTML tags (`<br />`, `<em>`, `<b>`) but these are pre-stored data, not reflected user input. No XSS.

  5. **`/api/Users/{id}`**: Returns 401 without authentication. Cannot test for XSS without valid JWT Bearer token.

- **Conclusion**: No reflected XSS vulnerabilities found on any tested additional endpoints.