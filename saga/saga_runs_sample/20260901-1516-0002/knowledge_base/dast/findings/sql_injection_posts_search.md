# SQL Injection in /posts?search

**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** GET `/posts?search=`
**Vulnerable Parameter:** `search` (query string)
**Detection Payload:** `'` (single quote)
**Evidence:** HTTP 200 response containing visible MySQL error:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%' ' at line 1")
```
**Notes:** The single quote breaks a LIKE-based search query on the posts search endpoint. The error is displayed directly in the HTML response body.