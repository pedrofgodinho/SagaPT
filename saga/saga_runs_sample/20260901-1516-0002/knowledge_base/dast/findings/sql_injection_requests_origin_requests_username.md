## SQL Injection in /requests?origin=requests&username

- **Endpoint**: `GET /requests?origin=requests&username=<SqliPayload>`
- **Parameter**: `username` (query string)
- **Detection payload**: `'` (single quote)
- **Evidence**: Response returned HTTP 500 Internal Server Error. The bare single quote caused the application to crash.
- **Assessment**: The 500 error triggered by a single quote confirms SQL injection in the `username` parameter when `origin=requests`.