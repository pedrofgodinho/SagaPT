## CORS Wildcard on All Endpoints

**Endpoint:** All endpoints on http://juiceshop.local:3000
**Vulnerability Class:** Cross-Origin Misconfiguration (CORS)

### Evidence
Every tested endpoint returns `Access-Control-Allow-Origin: *`:
- `GET /` → 200, CORS header present
- `GET /admin` → 200, CORS header present
- `GET /rest/user/me` → 500, CORS header present
- `GET /rest/user/login` → 401, CORS header present
- `GET /ftp/acquisitions.md` → 200, CORS header present
- `GET /ftp/incident-support.kdbx` → 200, CORS header present
- `POST /rest/user/login` → 401, CORS header present

### Analysis
The application uses a wildcard CORS policy (`Access-Control-Allow-Origin: *`) on ALL endpoints, including sensitive authentication endpoints. Notably, **no `Access-Control-Allow-Credentials: true` header is present**, which means browsers will NOT send cookies or auth tokens with cross-origin requests. This limits the practical impact but still represents a misconfiguration.

Additionally, **no `Access-Control-Allow-Methods` or `Access-Control-Allow-Headers` restrictions** are enforced.

### Impact
- Any cross-origin web application can read responses from this server
- While credentials (cookies) won't be sent automatically by browsers, any pre-authenticated requests made from a malicious page could still be read
- Sensitive endpoints (/rest/user/login, /rest/user/me) are not excluded from CORS

### Mitigation
Restrict CORS to specific trusted origins. Exclude sensitive endpoints from CORS entirely.