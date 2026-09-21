## Reflected XSS Testing on /api/Products - No Reflection Found

**Endpoint:** GET /api/Products
**Vulnerability Class:** Reflected XSS (not confirmed)

### Tests Performed
- `GET /api/Products?search=<script>alert(1)</script>` → 200, full catalog returned (search param ignored)
- `GET /api/Products?search=<img src=x onerror=alert(1)>` → 200, full catalog returned (search param ignored)
- `GET /api/Products?name=<script>alert(1)</script>` → 200, empty data array (name param filters but no reflection)
- `GET /api/Products?name=' OR '1'='1` → 200, empty data array (no SQL error)
- `GET /api/Products?name=';--` → 200, empty data array (no SQL error)
- `GET /api/Products?name=' AND 1=1--` → 200, empty data array (no SQL error)
- `GET /?search=<script>alert(1)</script>` → 200, main page returned (SPA, no reflection)
- `GET /ftp/acquisitions.md<script>alert(1)</script>` → 403 (extension filter)

### Evidence
- The `search` query parameter is accepted but ignored (returns full product catalog regardless of input)
- The `name` query parameter filters results but does not reflect input in the response
- No XSS payloads are reflected in any response body
- No ZAP XSS alerts triggered on any request

### Conclusion
No reflected XSS vulnerability confirmed on the tested input parameters. The API does not reflect user input in responses. The SPA frontend may handle input differently, but the API layer does not exhibit reflected XSS.