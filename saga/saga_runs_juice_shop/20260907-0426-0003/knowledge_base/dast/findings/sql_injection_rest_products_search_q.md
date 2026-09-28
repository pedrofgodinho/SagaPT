# SQL Injection in /rest/products/search?q=

## Vulnerability Class
SQL Injection (Error-based)

## Endpoint
`GET /rest/products/search?q=`

## Vulnerable Parameter
`q` (query string parameter)

## Detection Payloads Tested
1. `'` (single quote) → 200, empty results (no error visible — may be caught by app logic)
2. `' OR 1=1 -- ` → **500 Internal Server Error**: `SQLITE_ERROR: incomplete input`
3. `' UNION SELECT NULL -- ` → **500 Internal Server Error**: `SQLITE_ERROR: near "UNION": syntax error`
4. `' OR SLEEP(5) -- ` → **500 Internal Server Error**: `SQLITE_ERROR: incomplete input`

## Evidence
- The `' UNION SELECT NULL --` payload produced a clear SQLite syntax error: `SQLITE_ERROR: near "UNION": syntax error` (HTTP 500). This confirms the `q` parameter value is interpolated directly into a SQL query without proper parameterization.
- The database is **SQLite** (confirmed by Sequelize ORM usage and error messages).
- Error messages reveal internal database error syntax, constituting information disclosure.

## Impact
Confirmed injectable SQL parameter. An attacker could potentially extract data via UNION-based injection, error-based extraction, or boolean/time-based blind injection.

## Not Vulnerable
The second endpoint `/api/Products?searchTerm=` was also tested with the same payloads (single quote, `' OR 1=1 --`, `' UNION SELECT NULL --`) and returned identical 200 responses with the same ETag across all attempts, indicating the parameter is properly parameterized or sanitized. No SQL injection detected on that endpoint.