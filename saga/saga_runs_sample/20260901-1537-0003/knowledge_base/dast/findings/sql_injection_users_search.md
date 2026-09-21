## SQL Injection in /users?search

- **Endpoint:** GET /users
- **Parameter:** search
- **Detection payload:** `'` (single quote appended)
- **Evidence:** Response returned HTTP 200 with a visible MySQL error message: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''' at line 1")`
- **Type:** Error-based SQL injection
- **Priority:** High — visible SQL error message exposes database syntax details