## SQL Injection in /friends?username=XXX&search=XXX

- **Endpoint:** `GET http://www.hackergram.com/friends?username=mr_robot&search=`
- **Parameter:** `search` (query string)
- **Detection payload:** `' trash`
- **Evidence:** Response contains MySQL error: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash' AND username IN (SELECT username1 FROM Friends WHERE username2 = 'mr_ro' at line 1"`)
- **Response status:** 200 with visible SQL error in page body
- **Severity:** High — the application returns raw database error messages to the user, confirming the `search` parameter is concatenated into a SQL query without parameterization. The error also reveals internal query structure (`AND username IN (SELECT username1 FROM Friends WHERE username2 = ...)`), indicating a subquery is involved.