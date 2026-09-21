## SQL Injection in /profile?username

- **Endpoint**: `GET /profile?username=<SqliPayload>`
- **Parameter**: `username` (query string)
- **Detection payload**: `'` (single quote)
- **Evidence**: Response returned HTTP 200 with a visible MySQL error message:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''''' at line 1")
  ```
- **Assessment**: The single quote breaks the SQL query, confirming the `username` parameter is concatenated into a SQL query without parameterization. This is a clear SQL injection vulnerability.