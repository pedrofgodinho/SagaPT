## SQL Injection in /friends?username

- **Endpoint**: `GET /friends`
- **Parameter**: `username` (query string)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `'%20trash` (single quote followed by space and "trash" appended to the username parameter)
- **Evidence**: The application returned a visible MySQL error in the response body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash'  UNION SELECT username2 FROM Friends  WHERE username1 = '' trash'")
  ```
  The error reveals the underlying query structure: a `UNION SELECT username2 FROM Friends WHERE username1 = '<input>'` pattern.
- **HTTP Status**: 200 (error message rendered in the page body in a red `<h4>` element)
- **ZAP Alert**: Application Error Disclosure (pluginId 90022)
- **Impact**: An attacker can inject arbitrary SQL into the friends list query, potentially reading, modifying, or deleting database contents. The error also leaks table/column names (`Friends`, `username1`, `username2`).
- **Root Cause**: User input is concatenated directly into SQL queries without parameterization or escaping.