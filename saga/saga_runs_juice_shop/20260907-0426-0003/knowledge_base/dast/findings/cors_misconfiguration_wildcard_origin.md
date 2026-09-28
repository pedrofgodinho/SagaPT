## CORS Misconfiguration - Wildcard Origin

**Vulnerability Class**: CORS Misconfiguration
**Endpoint**: All endpoints, tested on GET /rest/products/search?q=test

**Description**:
The application returns `Access-Control-Allow-Origin: *` (wildcard) on all tested endpoints, allowing any domain to make cross-origin requests. This is a misconfiguration as it permits unrestricted cross-origin access to API endpoints.

**Evidence**:
- `GET /rest/products/search?q=test` returns header: `Access-Control-Allow-Origin: *`
- `GET /ftp/acquisitions.md` returns header: `Access-Control-Allow-Origin: *`
- `GET /nonexistent-path-12345` returns header: `Access-Control-Allow-Origin: *`
- ZAP alert: "Cross-Domain Misconfiguration" (Medium confidence, Medium risk)

**Risk**: Medium - Any malicious website can make cross-origin requests to this application's API, potentially reading sensitive data via the browser's CORS mechanism.