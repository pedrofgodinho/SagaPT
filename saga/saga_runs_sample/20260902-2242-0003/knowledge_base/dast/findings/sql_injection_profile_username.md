**Vulnerability Class:** SQL Injection (Error-based)

**Endpoint:** GET `/profile?username=`

**Vulnerable Parameter:** `username`

**Detection Payload:** `admin' trash` (URL-encoded: `admin%27%20trash`)

**Evidence:** The response (HTTP 200) contains a visible MySQL error message in the page body:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash'' at line 1")
```

**Impact:** An attacker can inject arbitrary SQL into the user profile query, potentially reading, modifying, or deleting data from the database.

**Confidence:** High — clear MySQL error confirming unparameterized query concatenation.