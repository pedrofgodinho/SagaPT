## SQL Injection in /friends?username

- **Endpoint:** GET /friends
- **Parameter:** username
- **Detection payload:** `admin'` (single quote appended)
- **Evidence:** Response returned HTTP 200 with a visible MySQL error message:
  `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'admin'')' at line 1")`
- **Additional confirmation:** Payload `' OR '1'='1` returned a list of all friends (6 users shown), while `' AND '1'='1` returned "No friends." — confirming boolean-based injection behavior.
- **Type:** Error-based and boolean-based SQL injection
- **Priority:** High — visible SQL error message exposes database syntax details