## SQL Injection in /posts?search

- **Endpoint**: `GET /posts`
- **Parameter**: `search` (query string)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `%27` (single quote appended to the search parameter)
- **Evidence**: The application returned a visible MySQL error in the response body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''' at line 1")
  ```
  Note: The endpoint also returns a 500 error with an empty search value, but the single quote produces a 200 response with a clear SQL syntax error.
- **HTTP Status**: 200 (error message rendered in a red `<h4>` element)
- **ZAP Alert**: Application Error Disclosure (pluginId 90022)
- **Impact**: An attacker can inject arbitrary SQL into the posts search query, potentially reading, modifying, or deleting database contents.
- **Root Cause**: User input is concatenated directly into SQL queries without parameterization or escaping.