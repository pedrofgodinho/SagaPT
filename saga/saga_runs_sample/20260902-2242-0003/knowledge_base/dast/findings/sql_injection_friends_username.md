**Vulnerability Class:** SQL Injection (Error-based)

**Endpoint:** GET `/friends?username=`

**Vulnerable Parameter:** `username`

**Detection Payload:** `admin' trash` (URL-encoded: `admin%27%20trash`)

**Evidence:** The response (HTTP 200) contains a visible MySQL error message:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash'  UNION SELECT username2 FROM Friends  WHERE username1 = 'admin' trash' at line 1")
```
The error reveals the underlying query structure: `...UNION SELECT username2 FROM Friends WHERE username1 = 'admin' ...`, confirming the parameter is directly concatenated into a SQL query.

**Impact:** An attacker can inject arbitrary SQL into the friends list query, potentially reading, modifying, or deleting data from the database.

**Confidence:** High — clear MySQL error confirming unparameterized query concatenation.