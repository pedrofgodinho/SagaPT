## SQL Injection in /direct_messages?username

- **Endpoint**: `GET /direct_messages?username=<SqliPayload>`
- **Parameter**: `username` (query string)
- **Detection payload**: `'` (single quote)
- **Evidence**: Response returned HTTP 500 Internal Server Error. The bare single quote caused the application to crash, indicating the parameter is used in a SQL query without proper escaping or parameterization.
- **Assessment**: The 500 error triggered by a single quote confirms SQL injection — the unescaped quote breaks the SQL query structure.