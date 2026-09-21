## SQL Injection in /remove_request (POST)

- **Endpoint**: `POST /remove_request`
- **Parameter**: `username` (form field)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `'` (single quote appended to benign username)
- **Evidence**: The application returned a visible MySQL error in the response body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'mr_robot') OR (username1 = 'mr_robot' AND username2 = 'mr_robot''')' at line 1")
  ```
  The error reveals the underlying query structure: a boolean condition pattern `(username1 = '<input>') OR (username1 = '<origin>' AND username2 = '<input>')`.
- **HTTP Status**: 200 (error message rendered in the page body in a red `<h4>` element)
- **ZAP Alert**: Application Error Disclosure (pluginId 90022)
- **Impact**: An attacker can inject arbitrary SQL into the remove request query, potentially reading, modifying, or deleting database contents. The error also leaks table/column names (`Friends`, `username1`, `username2`).
- **Root Cause**: User input in the `username` form field is concatenated directly into SQL queries without parameterization or escaping.
- **Note**: The `origin` parameter was also tested with `'` and did NOT trigger SQL errors — it appears to be safe.