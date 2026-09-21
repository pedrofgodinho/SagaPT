# SQL Injection in POST /create_post

**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** POST `/create_post`
**Vulnerable Parameter:** `content` (form field)
**Detection Payload:** `'` (single quote)
**Content-Type:** application/x-www-form-urlencoded
**Evidence:** HTTP 200 response containing visible MySQL error:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''')' at line 1")
```
**Notes:** The single quote in the content form field breaks a SQL INSERT query when creating a new post. The error is displayed directly in the HTML response body.