## Vulnerability: Blind SQL Injection in Login Email Field

**Endpoint:** `POST /rest/user/login`
**Parameter:** `email`
**Vulnerability Class:** SQL Injection (Blind/Boolean-based)

### Description
The login email parameter is vulnerable to SQL injection. When a malicious payload is submitted, the application returns a 500 Internal Server Error with a Sequelize/SQLite stack trace, confirming the input is being processed by the database layer without proper parameterization.

### Detection Payload
```
POST /rest/user/login
Content-Type: application/json

{"email": "' trash", "password": "test"}
```

### Evidence
- Payload `' trash` → HTTP 500 with Sequelize stack trace:
  ```
  at Database.<anonymous> (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27)
  at Query.run (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:183:12)
  ```
- Payload `' UNION SELECT sqlite_version()-- ` → HTTP 500 with same SQLite stack trace
- Normal payload `admin'-- ` → HTTP 401 (expected auth failure, no SQL error)

### DB Technology
SQLite (confirmed via Sequelize SQLite dialect in stack trace)

### Impact
An attacker can extract data, bypass authentication, or potentially execute arbitrary SQL commands through the login endpoint.

### Risk
High - SQL injection on authentication endpoint can lead to full database compromise.