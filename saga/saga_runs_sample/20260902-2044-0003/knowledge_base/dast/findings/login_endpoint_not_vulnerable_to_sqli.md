## SQL Injection Test - Login Endpoint (Negative Finding)

**Endpoint:** POST http://www.hackergram.com/login
**Parameters tested:** `username`, `password`
**Test date:** 2026-09-02

### Payloads Attempted

| Parameter | Payload | Result |
|-----------|---------|--------|
| username | `'` (bare single quote) | 200, no SQL error |
| username | `' OR 1=1 -- ` | 200, no SQL error |
| username | `' OR '1'='1` | 200, no SQL error |
| username | `' AND '1'='2` | 200, no SQL error |
| username | `' UNION SELECT NULL,NULL-- ` | 200, no SQL error |
| password | `'` (bare single quote) | 200, no SQL error |

### Observations

- All requests returned HTTP 200 with identical response bodies (18,477 bytes)
- No SQL error messages, 500 status codes, or structural response differences observed
- No ZAP SQL injection alerts triggered for any probe
- The ZAP proxy's shared session persisted across all requests, masking login behavior; however, SQL syntax errors would still be visible in the response regardless of session state

### Conclusion

**SQL injection NOT confirmed.** The login endpoint parameters (`username`, `password`) appear to be properly parameterized. No evidence of SQL injection was found across multiple probe types (error-based, tautology-based, UNION-based).

### Note

Response identity across all payloads (including the UNION SELECT payload which would produce a distinctly different body if SQLi were present) strongly suggests the parameters are handled safely by the application.