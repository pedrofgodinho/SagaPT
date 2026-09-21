## SQL Injection in /profile?username

- **Endpoint:** `/profile`
- **Parameter:** `username` (GET query parameter)
- **Vulnerability Class:** SQL Injection (Error-based)
- **Detection Payload:** `username=mr_robot' trash`
- **Evidence:** The response (HTTP 200) contains a visible MySQL error message:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash'' at line 1")
  ```
  The same error occurs with `username=admin' trash`, confirming the parameter is unparameterized and directly concatenated into SQL.
- **Impact:** Confirmed injectable. An attacker can manipulate SQL queries to read, modify, or delete database contents.