## SQL Injection in Login Email Field

**Endpoint:** POST /rest/user/login
**Parameter:** email
**Vulnerability Class:** SQL Injection (Authentication Bypass)

### Detection Payload
```json
{"email": "' OR '1'='1", "password": "ReconPass123!"}
```

### Evidence
- **Normal request** with valid credentials returns 200 with JWT token
- **SQLi payload** `' OR '1'='1` in email field also returns 200 with valid JWT token, authenticating successfully without knowing the correct password
- The single quote breaks out of the SQL query structure and the OR condition bypasses authentication

### Impact
An attacker can bypass authentication entirely by injecting SQL in the email field, gaining unauthorized access to any account (or acting as a generic authenticated user).

### Note
The login endpoint path is `/rest/user/login`, not `/api/authenticate/login` as listed in recon findings.