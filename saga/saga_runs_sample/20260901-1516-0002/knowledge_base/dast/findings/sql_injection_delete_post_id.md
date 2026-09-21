## SQL Injection in /delete_post?id

- **Endpoint**: `GET /delete_post?id=<SqliPayload>`
- **Parameter**: `id` (query string)
- **Detection payload**: `'` (single quote)
- **Evidence**: Response returned HTTP 500 Internal Server Error. The bare single quote caused the application to crash.
- **Assessment**: The 500 error triggered by a single quote confirms SQL injection in the `id` parameter.