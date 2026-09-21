## SQL Injection in /profile?username

- **Endpoint:** GET /profile
- **Parameter:** username
- **Detection payload:** `admin'` (single quote appended)
- **Evidence:** Response returned HTTP 200 with a visible MySQL error message:
  `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''admin''' at line 1")`
- **Additional confirmation:** Payload `' OR '1'='1` returned a different response (full profile page with many posts, Content-Length 15930) vs `' AND '1'='1` which returned fewer posts (Content-Length 5676), indicating boolean-based behavior consistent with SQL injection.
- **Type:** Error-based and boolean-based SQL injection
- **Priority:** High — visible SQL error message exposes database syntax details