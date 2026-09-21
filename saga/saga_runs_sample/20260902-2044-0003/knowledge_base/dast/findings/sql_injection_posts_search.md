# SQL Injection in /posts search parameter

- **Vulnerability Class:** SQL Injection (Error-based)
- **Endpoint:** GET /posts
- **Parameter:** `search` (query parameter)
- **Detection Payload:** `'` (single quote appended to search parameter value)
- **Evidence:** Response (HTTP 200) contained visible MySQL error message in HTML body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''' at line 1")
  ```
- **Risk:** High — SQL error confirms the parameter is concatenated into a SQL query without proper parameterization.