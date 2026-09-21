**Vulnerability:** SQL Injection in POST `/create_post` content field

**Endpoint:** POST /create_post

**Parameter:** content (form field)

**Detection Payload:** test' (single quote appended)

**Evidence:** The response returned HTTP 200 with a visible MySQL error message:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''test'') at line 1")
```

**Impact:** The content parameter is concatenated into a SQL query without parameterization, allowing an attacker to alter query structure.

**Risk:** High — visible SQL error confirms injectability.