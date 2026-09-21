## SQL Injection in Login Password Field

- **Endpoint:** POST http://juiceshop.local:3000/rest/user/login
- **Parameter:** password
- **Vulnerability Class:** SQL Injection (SQLi)
- **Detection Payload:** `' OR '1'='1' -- ` in the password field
- **Evidence:** Normal login attempt (invalid credentials) returns HTTP 401 with "Invalid email or password." The SQLi payload in the password field returned HTTP 200 with a valid authentication JWT token in the response body, including `authentication.token`, `bid: 1`, and `umail: "admin@juice-sh.op"`. This structurally different response confirms the password parameter is also injectable into a SQL query without parameterization.
- **Impact:** Attacker can bypass authentication via the password field as well as the email field, logging in as any user (including admin) without knowing credentials.
- **Priority:** HIGH - visible SQL injection in the password field resulting in authentication bypass.