**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** POST `/request_friend`
**Parameter:** `username`
**Detection Payload:** `'` (single quote appended to value, e.g. `test'`)
**Evidence:** Response returned HTTP 500 Internal Server Error — the unhandled exception is caused by the single quote breaking the SQL query. This is a classic sign of SQL injection where the database throws an error that is not caught by the application.
**HTTP Status:** 500 Internal Server Error
**Risk:** High — the `username` parameter is directly concatenated into a SQL query without parameterization.