## SQL Injection in edit_post GET endpoint (id parameter)

- **Endpoint**: `GET http://www.hackergram.com/edit_post`
- **Parameter**: `id` (query parameter)
- **Vulnerability class**: SQL Injection (MySQL)
- **Detection payload**: `'` (bare single quote, URL-encoded as `%27`)
- **Evidence**:
  - Baseline (benign id=19): Status 200, response body ~4,356 bytes, edit post form rendered normally
  - Payload (id=19'): Status 500, response body ~265 bytes, generic "Internal Server Error"
  - The drastic difference in status code (200 → 500) and response body size confirms the `id` parameter is concatenated into a SQL query without parameterization.
- **Database**: MySQL (500 error consistent with unhandled MySQL syntax error)
- **Risk**: High — unparameterized query allows further exploitation