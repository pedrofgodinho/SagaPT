**Vulnerability:** SQL Injection in POST `/remove_request` username field

**Endpoint:** POST /remove_request

**Parameter:** username (form field)

**Detection Payload:** test' (single quote in username field)

**Evidence:** The response returned HTTP 200 with a visible MySQL error message:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'mr_robot') OR (username1 = 'mr_robot' AND username2 = 'test'') at line 1")
```

The error reveals the full SQL structure being used, confirming the username parameter is directly concatenated into a SQL query.

**Impact:** The parameter is concatenated into a SQL query without parameterization, allowing an attacker to alter query structure.

**Risk:** High — visible SQL error confirms injectability.