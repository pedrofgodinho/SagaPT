**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** POST `/create_post`
**Parameter:** `content`
**Detection Payload:** `'` (single quote appended to value, e.g. `test'`)
**Evidence:** Response returned HTTP 200 with visible MySQL error message in page body: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''test')' at line 1")` — the single quote breaks the SQL query, confirming the parameter is directly concatenated into a SQL query.
**HTTP Status:** 200 with SQL error displayed in page body
**Risk:** High — the `content` parameter is directly concatenated into a SQL query without parameterization.