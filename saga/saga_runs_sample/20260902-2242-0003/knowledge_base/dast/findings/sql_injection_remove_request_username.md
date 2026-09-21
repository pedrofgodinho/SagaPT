## SQL Injection in /remove_request — POST `username` parameter

- **Vulnerability Class:** SQL Injection (Error-based)
- **Endpoint:** POST `/remove_request`
- **Vulnerable Parameter:** `username` (form field)
- **Detection Payload:** `admin' trash`
- **Evidence:** The request returns HTTP 200 with a visible MySQL error message in the page body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash' AND username2='mr_robot') OR (username1 = 'mr_robot' AND username2 = 'adm' at line 1")
  ```
  ZAP also raised an "Application Error Disclosure" alert. The error reveals the underlying query structure with `AND username2=` and `OR username1=` conditions, confirming the `username` parameter is directly concatenated into a SQL query without proper parameterization.
- **Impact:** An attacker can inject arbitrary SQL into the remove_request query, potentially reading, modifying, or deleting data from the database.
- **Confidence:** High — clear MySQL syntax error confirming unparameterized query concatenation.