# SQL Injection in Login Email Field

**Endpoint:** POST /rest/user/login
**Vulnerable Parameter:** email
**Vulnerability Class:** SQL Injection

## Evidence
The email parameter is not parameterized in the SQL query. Sending the payload `' trash` triggers a SQLite/Sequelize error:
- Status: 500 Internal Server Error
- Error body reveals: SQLite/Sequelize stack trace from `/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js`
- This confirms the input is concatenated into SQL without proper escaping.

## Detection Payload
```
POST /rest/user/login
{"email": "' trash", "password": "ReconPass123"}
```

## Impact
An attacker can bypass authentication, extract data, or modify the database. The injection point allows full SQL query manipulation.

## Notes
The password field does NOT appear to be SQLi-injectable (returns 401 "Invalid email or password" with payload `' trash`). Only the email field is vulnerable.