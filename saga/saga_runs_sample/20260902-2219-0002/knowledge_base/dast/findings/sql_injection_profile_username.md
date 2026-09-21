## SQL Injection in /profile?username

- **Endpoint**: `GET /profile`
- **Parameter**: `username` (query string)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `mr_robot'` (single quote appended to benign value)
- **Evidence**: The application returned a visible MySQL error in the response body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''mr_robot''' at line 1")
  ```
- **HTTP Status**: 200 (error message rendered in the page body)
- **ZAP Alert**: Application Error Disclosure (pluginId 90022)
- **Impact**: An attacker can inject arbitrary SQL into queries, potentially reading, modifying, or deleting database contents.
- **Root Cause**: User input is concatenated directly into SQL queries without parameterization or escaping.