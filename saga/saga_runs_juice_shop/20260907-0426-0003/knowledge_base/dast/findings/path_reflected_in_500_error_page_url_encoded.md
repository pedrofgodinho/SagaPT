# Path Reflected in 500 Error Page (URL-Encoded - Not XSS)

- **Endpoint**: `GET /api/<any-unmatched-path>`
- **Observation**: The Express 500 error page reflects the URL path in the HTML response body.
- **Evidence**: Request to `/api/%3Cscript%3Ealert(1)%3C/script%3E` returns:
  ```
  <h2><em>500</em> Error: Unexpected path: /api/%3Cscript%3Ealert(1)%3C/script%3E</h2>
  ```
- **Analysis**: While the path is reflected in an HTML context, XSS payloads are **URL-encoded** (`%3C` instead of `<`). The `%3Cscript%3E` sequence is NOT a valid HTML entity and will render as literal text in the browser. This is **NOT** a confirmed XSS vulnerability.
- **Content-Type**: `text/html; charset=utf-8` (HTML context)
- **Status**: 500 Internal Server Error
- **Note**: The URL-encoded reflection means an attacker cannot inject executable HTML/JavaScript via the path. The encoding is performed by the Express framework's error handler.

- **Related**: This endpoint is also vulnerable to information disclosure (stack traces, Express version) but that is a separate finding.