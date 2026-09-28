# SQL Injection Testing on Authenticated Endpoints — Blocked by JWT Authentication Tooling

## Scope
Tested SQL injection on the following authenticated endpoints of OWASP Juice Shop:
- `POST /api/Complaints` (parameter: `message`)
- `POST /api/BasketItems` (parameters: `productId`, `quantity`)
- `GET /api/Users/{id}` (path parameter: user ID)

## Results

### All Three Endpoints
- **Result**: HTTP 401 "UnauthorizedError: No Authorization header was found"
- **Payloads tested on GET /api/Users/1**:
  - `/api/Users/1 OR 1=1 --` → 401 (identical to baseline)
  - `/api/Users/1' OR '1'='1` → 401 (identical to baseline)
- **Payloads tested on POST /api/Complaints**:
  - `{"message": "This is a normal test message."}` → 401
  - `{"message": "' OR 1=1 --"}` → 401 (same response)
- **Payloads tested on POST /api/BasketItems**:
  - `{"productId": 1, "quantity": 1}` → 401 (same response)

## Root Cause
The JWT token is returned in the JSON response body (`authentication.token`), **not as an HttpOnly cookie**. The `login()` tool (which restores cookie-based sessions) returns 0 cookies. The `http_get` and `http_post` tools do not support custom headers, making it impossible to attach `Authorization: Bearer <JWT>`.

## Evidence
- Recon agent's `login_test_user_raw.json` shows JWT in response body: `"authentication":{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."}`
- All authenticated endpoint requests return identical 401 HTML error page regardless of payload
- Byte-for-byte identical responses across all attempts confirm the SQL layer is never reached

## Impact
**SQL injection could NOT be confirmed or denied** on these authenticated endpoints due to the tooling limitation of not being able to attach JWT Bearer tokens. The endpoints likely use Sequelize ORM (parameterized queries), but this cannot be verified without authenticated access.

## Comparison with Previous DAST
This is the same blocking issue confirmed by the earlier DAST agent (`sqli_auth_endpoints_blocked_by_middleware.md`), which also could not test these endpoints.

## Not Vulnerable (Confirmed)
- The SQL injection payloads never reach the SQL layer — they are blocked at the authentication middleware level.
- The `POST /rest/user/login` endpoint (email field) and `GET /rest/products/search?q=` are the only confirmed SQL injection points (tested and confirmed by previous DAST invocations).