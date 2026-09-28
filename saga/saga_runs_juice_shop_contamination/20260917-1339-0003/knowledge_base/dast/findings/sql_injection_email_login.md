## SQL Injection in Login Email Field

**Endpoint:** POST /rest/user/login
**Parameter:** email (JSON body)
**Vulnerability Class:** SQL Injection (Error-based)

### Detection Payloads

1. **Bare single quote** (error trigger):
   - Payload: `' trash`
   - Response: HTTP 500 with SQLite/Sequelize stack trace
   - Evidence: Response body contains stack trace referencing `/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185`

2. **OR-based authentication bypass**:
   - Payload: `' OR '1'='1' -- `
   - Response: HTTP 200 with valid JWT authentication token
   - Evidence: Returned `authentication.token` field and `umail: "admin@juice-sh.op"` — successfully authenticated as admin user

### Impact
An attacker can bypass authentication entirely by injecting SQL in the email field, gaining access to any account (including admin) without knowing credentials.

### Notes
- The `password` field was also tested with the same payloads but returned 401 — only the `email` parameter is vulnerable.
- The application uses SQLite with Sequelize ORM, and the email parameter is not properly parameterized before query execution.