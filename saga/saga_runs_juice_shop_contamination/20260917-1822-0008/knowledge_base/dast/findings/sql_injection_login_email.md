## SQL Injection in Login Email Field

- **Endpoint:** POST http://juiceshop.local:3000/rest/user/login
- **Parameter:** email
- **Vulnerability Class:** SQL Injection (SQLi)
- **Detection Payload:** `' OR '1'='1' -- `
- **Evidence:** Normal login attempt returns HTTP 401 with body "Invalid email or password." The SQLi payload returned HTTP 200 with a valid authentication JWT token in the response body, including `authentication.token`, `bid: 1`, and `umail: "admin@juice-sh.op"`. This structurally different response confirms the email parameter is injectable into a SQL query without parameterization.
- **Impact:** Attacker can bypass authentication entirely and log in as any user (including admin) without knowing credentials.
- **Priority:** HIGH - visible SQL injection resulting in authentication bypass.