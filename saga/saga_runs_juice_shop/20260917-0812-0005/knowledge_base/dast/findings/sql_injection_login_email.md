## SQL Injection in Login Email Parameter

**Endpoint:** `POST http://juiceshop.local:3000/rest/user/login`
**Parameter:** `email`
**Vulnerability Class:** SQL Injection (Error-based)
**Database:** SQLite (via Sequelize ORM)

### Detection Payload
```json
{"email": "' trash", "password": "test"}
```

### Evidence
- **Normal request** (valid format email/password): Returns **401** with body `Invalid email or password.` (26 bytes)
- **With `' trash` payload** (JSON content type): Returns **500 Internal Server Error** with an HTML error page containing a stack trace:
  ```
  at Database.<anonymous> (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27)
  at /juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:183:50
  at Query.run (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:183:12)
  ```
- **With `' trash` payload** (form-urlencoded content type): Identical **500** response with the same stack trace.

### Analysis
The single quote in the `email` parameter breaks the SQL query syntax, causing SQLite to throw a query error that is exposed in the application's error page. This confirms the email parameter is concatenated into a SQL query without proper parameterization. The stack trace reveals the app uses Sequelize ORM with SQLite as the database backend.

### Password Parameter
The `password` parameter was also tested with the same payload (`' trash`) and returned a normal 401 response — it does not appear to be vulnerable to SQL injection.

### Content Types Tested
- `application/json` — vulnerable
- `application/x-www-form-urlencoded` — vulnerable

### Authentication Bypass Attempts
Payloads such as `' OR '1'='1` and `admin@juiceshop.local' -- ` both returned 401, indicating that despite the SQL injection vulnerability, the authentication logic prevents actual bypass (likely due to how Sequelize handles the query or additional validation).