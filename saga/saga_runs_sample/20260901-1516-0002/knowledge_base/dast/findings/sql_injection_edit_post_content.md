# SQL Injection in POST /edit_post

**Vulnerability Class:** SQL Injection (Error-based)
**Endpoint:** POST `/edit_post`
**Vulnerable Parameter:** `content` (form field)
**Detection Payload:** `'` (single quote)
**Content-Type:** application/x-www-form-urlencoded
**Evidence:** HTTP 200 response containing visible MySQL error:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '19' ' at line 1")
```
**Notes:** The single quote in the content form field breaks a SQL UPDATE query when editing a post. Requires `id` parameter to be set to a post owned by the current user. The error is displayed directly in the HTML response body.