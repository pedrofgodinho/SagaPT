# SQL Injection in Login Email Field

- **Endpoint:** POST /rest/user/login
- **Parameter:** email
- **Vulnerability Class:** SQL Injection (SQLite via Sequelize ORM)
- **Detection Payload:** `' trash`
- **Evidence:** The payload caused a 500 Internal Server Error with a visible Sequelize/SQLite stack trace:
  - Stack trace references `/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185`
  - Response Content-Type: `text/html` (error page) instead of `application/json`
  - The error confirms user input is being concatenated into a SQL query without proper parameterization.
- **Impact:** An attacker could extract database contents, bypass authentication, or modify data.
- **Priority:** High — visible SQL error confirms injectability.