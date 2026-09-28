# SQL Injection on Login Email Field

- **Endpoint:** POST /rest/user/login
- **Vulnerable Parameter:** `email` field in JSON body
- **Detection Payload:** `{"email": "' trash", "password": "anything"}`
- **Evidence:** Returns HTTP 500 Internal Server Error with stack trace showing SQLite error at `/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27`. Normal login attempts return 401 "Invalid email or password."
- **Impact:** Confirmed SQL injection allows authentication bypass (verified with `' OR '1'='1'-- -` payload returning 200 with admin JWT token) and potential data extraction.
- **Risk:** Critical - Authentication bypass confirmed, full database compromise possible