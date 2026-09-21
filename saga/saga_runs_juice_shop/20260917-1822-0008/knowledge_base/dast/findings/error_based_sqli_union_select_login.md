## Error-Based SQL Injection via UNION SELECT in Login Email

- **Endpoint:** POST http://juiceshop.local:3000/rest/user/login
- **Parameter:** email
- **Vulnerability Class:** SQL Injection (Error-Based)
- **Detection Payload:** `' UNION SELECT 1,2,3--` in the email field
- **Evidence:** Normal login returns HTTP 401. The UNION SELECT payload returned HTTP 500 Internal Server Error with a stack trace referencing `/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27`, confirming a SQL syntax error was triggered. This differs from the 401 responses returned by all other non-injecting payloads, confirming the email parameter is processed through a SQL query where UNION SELECT is not properly handled.
- **Impact:** Confirms the login endpoint is vulnerable to error-based SQL injection, which could be leveraged to extract database schema, credentials, or other sensitive data.
- **Priority:** HIGH - confirms SQL injection on the email parameter with a different technique (UNION SELECT error-based) from the previously identified boolean-based injection.