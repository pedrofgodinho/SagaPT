## SQL Injection in /create_post — POST `content` parameter

- **Vulnerability Class:** SQL Injection (Error-based)
- **Endpoint:** POST `/create_post`
- **Vulnerable Parameter:** `content` (form field)
- **Detection Payload:** `test' trash`
- **Evidence:** The request returns HTTP 200 with a visible MySQL error message in the page body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash')' at line 1")
  ```
  ZAP also raised an "Application Error Disclosure" alert. The error confirms the `content` parameter is directly concatenated into a SQL query without proper parameterization.
- **Impact:** An attacker can inject arbitrary SQL into the create_post query, potentially reading, modifying, or deleting data from the database.
- **Confidence:** High — clear MySQL syntax error confirming unparameterized query concatenation.