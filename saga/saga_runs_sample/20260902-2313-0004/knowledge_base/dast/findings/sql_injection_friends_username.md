## SQL Injection in /friends?username

- **Endpoint:** `/friends`
- **Parameter:** `username` (GET query parameter)
- **Vulnerability Class:** SQL Injection (Error-based)
- **Detection Payload:** `username=mr_robot' trash`
- **Evidence:** The response (HTTP 200) contains a visible MySQL error message that also reveals part of the underlying SQL query:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash' UNION SELECT username2 FROM Friends WHERE username1 = 'mr_robot' trash'' at line 1")
  ```
  The error exposes the table name `Friends` and column names `username1`, `username2`, confirming the parameter is unparameterized.
- **Impact:** Confirmed injectable. The error reveals database schema details (table/column names), increasing the severity.