## SQL Injection in /login (POST)

- **Endpoint**: `POST /login`
- **Parameter**: `password` (form field)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `'` (single quote appended to password)
- **Evidence**: The application returned a visible MySQL error in the response body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''test''' at line 1")
  ```
  The error reveals the query structure: `SELECT * FROM Users WHERE username = '<username>' AND password = '<input>'`.
- **HTTP Status**: 200 (error message rendered in the page body in a red `<h4>` element, alongside "Invalid username or password" flash message)
- **ZAP Alert**: Application Error Disclosure (pluginId 90022)
- **Impact**: An attacker can inject arbitrary SQL into the login password query, potentially bypassing authentication or reading, modifying, or deleting database contents.
- **Root Cause**: User input in the `password` form field is concatenated directly into SQL queries without parameterization or escaping.