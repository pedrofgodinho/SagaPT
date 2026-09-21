**Vulnerability Class:** SQL Injection (Error-based)

**Endpoint:** GET `/users?search=`

**Vulnerable Parameter:** `search`

**Detection Payload:** `admin' trash` (URL-encoded: `admin%27%20trash`)

**Evidence:** The response (HTTP 200) contains a visible MySQL error message:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash'' at line 1")
```

**Impact:** An attacker can inject arbitrary SQL into the user search query, potentially reading, modifying, or deleting data from the database.

**Confidence:** High — clear MySQL error confirming unparameterized query concatenation.