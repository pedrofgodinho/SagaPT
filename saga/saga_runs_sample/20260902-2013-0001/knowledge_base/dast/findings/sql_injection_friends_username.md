## SQL Injection in /friends?username

- **Endpoint:** `GET http://www.hackergram.com/friends?username=`
- **Parameter:** `username` (query string)
- **Detection payload:** `' trash`
- **Evidence:** Response contains MySQL error: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash' UNION SELECT username2 FROM Friends WHERE username1 = '' trash') at line 1"`
- **Response status:** 200 with visible SQL error in page body
- **Severity:** High — the error message reveals part of the underlying query structure (`UNION SELECT username2 FROM Friends WHERE username1 = ...`), confirming the parameter is concatenated into a SQL query. The application also leaks database schema information.