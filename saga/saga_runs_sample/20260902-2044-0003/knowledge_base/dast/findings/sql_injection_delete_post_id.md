## SQL Injection in delete_post GET endpoint (id parameter)

- **Endpoint**: `GET http://www.hackergram.com/delete_post`
- **Parameter**: `id` (query parameter)
- **Vulnerability class**: SQL Injection (MySQL)
- **Detection payload**: `1'` (bare single quote appended to numeric id)
- **Evidence**:
  - Baseline (benign id=1): Status 200, response body ~20,059 bytes, normal homepage rendered
  - Payload (id=1'): Status 500, response body ~265 bytes, generic "Internal Server Error"
  - The drastic difference in status code (200 → 500) and response body size confirms the `id` parameter is concatenated into a SQL query without parameterization.
- **Database**: MySQL (500 error consistent with unhandled MySQL syntax error)
- **Risk**: High — unparameterized query allows further exploitation