## SQL Injection in /users?search

- **Endpoint:** `GET http://www.hackergram.com/users?search=`
- **Parameter:** `search` (query string)
- **Detection payload:** `' trash`
- **Evidence:** Response contains MySQL error: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash'' at line 1"`)
- **Response status:** 200 with visible SQL error in page body
- **Severity:** High — the application returns raw database error messages to the user, confirming the `search` parameter is concatenated into a SQL query without parameterization.