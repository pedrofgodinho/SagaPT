## SQL Injection Leading to Authentication Bypass

**Endpoint:** `POST http://juiceshop.local:3000/rest/user/login`
**Parameter:** `email`
**Vulnerability Class:** SQL Injection (Authentication Bypass)
**Database:** SQLite (via Sequelize ORM)

### Detection Payload
```json
{"email": "' OR '1'='1' -- ", "password": "test"}
```

### Evidence
- **Normal request** with valid credentials: Returns **401** with `Invalid email or password.`
- **With `' OR '1'='1' -- ` payload**: Returns **200 OK** with a valid JWT authentication token for user ID 1 (admin role):
  ```json
  {"authentication":{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...","bid":1,"umail":"admin@juice-sh.op"}}
  ```
- **With `' OR 1=1 -- ` payload**: Also returns **200 OK** with admin JWT token.
- **With `admin@juiceshop.local' -- ` payload**: Returns 401 — comment-only bypass does not work.

### Analysis
The SQLi in the `email` parameter can be leveraged to bypass authentication entirely. The payloads `' OR '1'='1' -- ` and `' OR 1=1 -- ` return a valid JWT token for the admin user (id=1, role="admin"). This was not previously confirmed — the existing finding noted that auth bypass attempts returned 401, but these specific payloads succeed.

### Impact
An unauthenticated attacker can gain full administrative access to the application by injecting a SQL bypass payload in the login email field. This grants complete control over the application.

### Password Parameter
The `password` parameter was not tested for bypass — the email parameter alone is sufficient to authenticate as admin regardless of the password value.