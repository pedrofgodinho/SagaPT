## SQL Injection in POST /remove_request — username field

- **Endpoint**: POST /remove_request
- **Parameter**: username (hidden form field)
- **Detection Payload**: `test'` (single quote appended)
- **Evidence**: Response contains visible MySQL error message:
  `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'mr_robot') OR (username1 = 'mr_robot' AND username2 = 'test'' at line 1")`
- **HTTP Status**: 200 (with error displayed in page body)
- **Vulnerability Class**: Error-based SQL Injection
- **Priority**: High — visible SQL error messages directly confirm injectability