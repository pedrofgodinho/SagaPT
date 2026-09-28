## XSS Not Reflected on Search Endpoints

**Endpoint:** `GET http://juiceshop.local:3000/search?q=` and `GET http://juiceshop.local:3000/api/search?q=`
**Vulnerability Class:** Informational — No Reflected XSS

### Testing Performed
- Payload: `<script>alert(1)</script>`
- Payload: `<img src=x onerror=alert(1)>`

### Evidence
- `/search?q=<script>alert(1)</script>` returns **200** with the Angular SPA shell (9393 bytes). The XSS payload is NOT reflected in the response body.
- `/api/search?q=<img src=x onerror=alert(1)>` returns **500** "Unexpected path" — route not found.
- No ZAP XSS alerts triggered.

### Analysis
The search endpoint (`/search`) returns the SPA shell for all queries, indicating it is non-functional or search is handled client-side. The XSS payloads are not reflected in the server response.

### Impact
No reflected XSS vulnerability confirmed on the search endpoints via direct HTTP.