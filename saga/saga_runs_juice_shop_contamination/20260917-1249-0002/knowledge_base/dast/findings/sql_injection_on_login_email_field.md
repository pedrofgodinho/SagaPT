## SQL Injection on Login Email Field

- **Vulnerability Class:** SQL Injection
- **Endpoint:** POST /rest/user/login
- **Parameter:** email
- **Detection Payload:** `' trash`
- **Evidence:** The payload triggered a 500 Internal Server Error with a visible Sequelize/SQLite stack trace:
  ```
  at Database.<anonymous> (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27)
  at /juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:183:50
  ```
  This is a structurally different response compared to the normal 401 "Invalid email or password" response. The error confirms the email parameter is concatenated into a SQL query without parameterization.
- **Risk:** High — allows full database access
- **Note:** Password field tested with same payloads (`' trash`, `'' OR '''`) but returned 401 (normal), suggesting it may be parameterized.