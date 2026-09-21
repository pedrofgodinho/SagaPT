## SQL Injection in /friends?search

- **Endpoint**: GET /friends?username=&search=
- **Parameter**: search
- **Detection Payload**: `test'` (single quote appended)
- **Evidence**: Response contains visible MySQL error message:
  `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''%' AND username IN (SELECT username1 FROM Friends WHERE username2 = 'mr_robot' '' at line 1")`
- **HTTP Status**: 200 (with error displayed in page body)
- **Vulnerability Class**: Error-based SQL Injection
- **Priority**: High — visible SQL error messages directly confirm injectability