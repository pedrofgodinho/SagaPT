## Application Error Disclosure - Stack Traces

**Vulnerability Class:** Information Disclosure
**Endpoint:** POST /rest/user/login (and other endpoints)
**Evidence:**
- When SQL injection is triggered in the email field (bare `'`), the application returns HTTP 500 with a full Express.js stack trace
- Stack trace reveals file paths: `/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27`
- Stack trace reveals framework: Express ^4.22.1 with Sequelize ORM using SQLite
- Other endpoints (e.g., /api/Complaint, /api/Recycle) also return 500 with "Unexpected path" errors and stack traces
- /rest/user/whoami returns `{"user":{}}` when unauthenticated, confirming no active session

**Risk:** Stack traces reveal internal file paths, framework versions, and database technology, aiding attackers in crafting targeted exploits.