## SQL Injection in /edit_post?id=

- **Endpoint:** `GET /edit_post?id=XXX`
- **Parameter:** `id` (query string)
- **Detection payload:** `1'` (single quote appended to numeric id)
- **Evidence:** 
  - Benign request `id=1` returned HTTP 200 with normal page content.
  - Malicious request `id=1'` returned HTTP 500 Internal Server Error, indicating the single quote broke SQL query syntax.
- **Vulnerability class:** SQL Injection (error-based)
- **Risk:** High — confirms the `id` parameter is passed unsanitized into a SQL query.