**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** GET `/friends?username=<user>&search=`
**Parameter:** `search`
**Detection Payload:** `'` (single quote appended to value, e.g. `test'`)
**Evidence:** Response returned HTTP 200 with visible MySQL error message: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%' AND username IN (SELECT username1 FROM Friends WHERE username2 = 'mr_robot' '")` — the single quote breaks the SQL query, confirming the parameter is directly concatenated into a SQL query.
**HTTP Status:** 200 with SQL error displayed in page body
**Risk:** High — the `search` parameter is directly concatenated into a SQL query without parameterization.