## SQL Injection in POST /remove_request - username field

- **Endpoint:** POST /remove_request
- **Parameter:** username
- **Detection payload:** `stark'` (single quote appended to username value)
- **Evidence:** Response returned HTTP 200 with visible MySQL error message in body: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'mr_robot') OR (username1 = 'mr_robot' AND username2 = 'stark''')' at line 1")`
- **Type:** Error-based SQL injection — raw SQL error exposed in response body
- **Priority:** High — visible SQL error message exposes database syntax details