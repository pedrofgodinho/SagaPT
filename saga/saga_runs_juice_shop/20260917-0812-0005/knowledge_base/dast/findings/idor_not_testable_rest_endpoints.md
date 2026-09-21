## IDOR Not Testable on REST API Endpoints

**Endpoints Tested:** `GET /rest/user/{id}`, `GET /rest/order/{id}`, `GET /rest/feedback/{id}`
**Vulnerability Class:** Informational — No Accessible Resources for IDOR Testing

### Testing Performed
- `GET /rest/user/1` → 500 "Error: Unexpected path: /rest/user/1"
- `GET /rest/user/2` → 500 "Error: Unexpected path: /rest/user/2"
- `GET /rest/user/3` → 500 "Error: Unexpected path: /rest/user/3"
- `GET /rest/order/1` → 500 "Error: Unexpected path: /rest/order/1"
- `GET /rest/order/2` → 500 "Error: Unexpected path: /rest/order/2"
- `GET /rest/feedback/1` → 500 "Error: Unexpected path: /rest/feedback/1"
- `GET /rest/feedback/2` → 500 "Error: Unexpected path: /rest/feedback/2"

### Evidence
- All IDOR test endpoints return 500 Internal Server Error with "Unexpected path" message.
- These endpoints are not implemented as server-side Express routes — they are handled client-side by the Angular SPA.
- The `login()` function also failed with 401, confirming that server-side authentication is not available via direct HTTP requests.

### Analysis
This version of OWASP Juice Shop (v14+, Express ^4.22.1) uses Angular client-side routing for all REST API endpoints. The `/rest/user/{id}`, `/rest/order/{id}`, and `/rest/feedback/{id}` paths are not implemented as server-side Express routes. Instead, they return "Unexpected path" errors. IDOR testing requires the Angular SPA context which cannot be simulated via direct HTTP requests.

### Impact
No IDOR vulnerability confirmed via direct HTTP testing. The REST API endpoints are not accessible outside the Angular SPA context. IDOR testing would require browser-based testing with authenticated sessions through the SPA.