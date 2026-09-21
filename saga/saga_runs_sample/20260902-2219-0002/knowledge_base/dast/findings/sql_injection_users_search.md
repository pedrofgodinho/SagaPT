## SQL Injection in /users?search

- **Endpoint**: `GET /users`
- **Parameter**: `search` (query string)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `'` (single quote appended to the search parameter)
- **Evidence**: The application returned a visible MySQL error in the response body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''%'' at line 1")
  ```
- **HTTP Status**: 200 (error message rendered in the page body in a red `<h4>` element)
- **ZAP Alert**: Application Error Disclosure (pluginId 90022)
- **Impact**: An attacker can inject arbitrary SQL into user search queries, potentially reading, modifying, or deleting database contents.
- **Root Cause**: User input is concatenated directly into SQL queries without parameterization or escaping.