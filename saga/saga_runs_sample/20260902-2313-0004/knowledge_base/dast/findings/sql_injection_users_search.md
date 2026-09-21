## SQL Injection in /users?search

- **Endpoint:** `/users`
- **Parameter:** `search` (GET query parameter)
- **Vulnerability Class:** SQL Injection (Error-based)
- **Detection Payload:** `search=test' trash`
- **Evidence:** The response (HTTP 200) contains a visible MySQL error message:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash'' at line 1")
  ```
  This confirms the `search` parameter is directly concatenated into a SQL query without parameterization.
- **Impact:** Confirmed injectable. An attacker can manipulate SQL queries in the user search functionality.