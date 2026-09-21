**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** GET `/profile?username=`
**Parameter:** `username`
**Detection Payload:** `'` (single quote)
**Evidence:** Response contains MySQL error message: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '''' '''' at line 1")`
**HTTP Status:** 200 with SQL error displayed in page body
**Risk:** High — the `username` parameter is directly concatenated into a SQL query without parameterization, allowing an attacker to inject arbitrary SQL.