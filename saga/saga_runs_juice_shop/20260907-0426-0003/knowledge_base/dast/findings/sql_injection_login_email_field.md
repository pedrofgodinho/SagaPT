# SQL Injection in POST /rest/user/login (email field)

## Vulnerability Class
SQL Injection (Authentication Bypass)

## Endpoint
`POST /rest/user/login`

## Vulnerable Parameter
`email` (JSON body field)

## Detection Payload
`' OR 1=1 --`

## Evidence
- **Baseline** (invalid credentials): HTTP 401, body: `Invalid email or password.`
- **SQLi payload** (`' OR 1=1 --` in `email`, arbitrary password): HTTP 200, returned JWT token in `authentication.token` field.
- Decoded JWT payload reveals: `{"data":{"id":1,"username":"","email":"admin@juice-sh.op","role":"admin",...}}`
- This confirms the `email` parameter value is interpolated directly into a SQL query without proper parameterization, allowing authentication bypass.

## Not Vulnerable
- `password` field: Payloads `' OR 1=1 --` and `' OR '1'='1` both returned 401, indicating proper parameterization or sanitization.
- Alternative email payloads (`' OR '1'='1`, `admin@example.com' --`) returned 401.

## Impact
Confirmed injectable parameter enabling authentication bypass. An attacker can log in as any user (including admin) without knowing valid credentials by injecting always-true SQL conditions in the `email` field.