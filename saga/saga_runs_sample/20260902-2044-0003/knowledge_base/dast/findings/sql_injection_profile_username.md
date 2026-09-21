## SQL Injection in Profile Endpoint

- **Endpoint:** `GET /profile?username=`
- **Parameter:** `username` (query parameter)
- **Vulnerability Class:** SQL Injection (MySQL)
- **Detection Payload:** `mr_robot'` (bare single quote appended to a valid username)
- **Evidence:** The response body contains a raw MySQL error message:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''mr_robot'' at line 1")
  ```
- **HTTP Status:** 200 (error rendered in-page rather than returning 500)
- **Severity:** High — visible SQL error confirms the `username` parameter is directly concatenated into a SQL query without parameterization.
- **Notes:** ZAP also raised an "Application Error Disclosure" alert (plugin 90022). No data extraction or UNION-based probing was performed — detection only.