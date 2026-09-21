# SQL Injection in /friends?search

**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** GET `/friends?username=mr_robot&search=`
**Vulnerable Parameter:** `search` (query string)
**Detection Payload:** `'` (single quote)
**Evidence:** HTTP 200 response containing visible MySQL error:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%' AND username IN (SELECT username1 FROM Friends WHERE username2 = 'mr_robot' ' at line 1")
```
**Notes:** The single quote breaks the LIKE clause in a SQL query that searches friends list. The error is displayed directly in the HTML response body.