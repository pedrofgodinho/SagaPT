## XSS Not Reflected on Login Form Fields

**Endpoint:** `POST http://juiceshop.local:3000/rest/user/login`
**Parameters:** `email`, `password`
**Vulnerability Class:** Informational — No Reflected XSS

### Testing Performed
- Payload: `<script>alert(1)</script>` in `email` field (JSON content type) → 401 "Invalid email or password."
- Payload: `<script>alert(1)</script>` in `password` field (JSON content type) → 401 "Invalid email or password."
- Payload: `<img src=x onerror=alert(1)>` in `email` field (JSON content type) → 401 "Invalid email or password."
- Payload: `<script>alert(1)</script>` in `name` field of signup → 500 (non-functional route)
- Payload: `<img src=x onerror=alert(1)>` in `email` field of signup → 500 (non-functional route)
- Payload: `<script>alert(1)</script>` in `?search=` query parameter → 200 SPA shell, no reflection
- Payload: `<script>alert(1)</script>` in `?redirect=` query parameter → 200 SPA shell, no reflection

### Evidence
- All XSS payloads returned either the error message "Invalid email or password." (26 bytes) or the Angular SPA shell (9393 bytes).
- No user-supplied input was reflected in any HTTP response.
- No ZAP XSS alerts were triggered for any test request.

### Analysis
The application does not reflect user input back into HTTP responses. The login endpoint returns a fixed error message, and the Angular SPA shell is identical for all requests regardless of input. This is consistent with the existing finding for the search endpoint.

### Impact
No reflected XSS vulnerability confirmed on tested input points via direct HTTP requests.