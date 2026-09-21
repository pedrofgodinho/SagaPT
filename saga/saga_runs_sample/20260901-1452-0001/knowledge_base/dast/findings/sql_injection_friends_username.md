**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** GET `/friends?username=`
**Parameter:** `username`
**Detection Payload:** `'` (single quote appended to value, e.g. `mr_robot'`)
**Evidence:** Response returned HTTP 200 with visible MySQL error message: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'mr_robot''")` — the single quote breaks the SQL query, confirming the parameter is directly concatenated into a SQL query.
**HTTP Status:** 200 with SQL error displayed in page body
**Risk:** High — the `username` parameter is directly concatenated into a SQL query without parameterization.