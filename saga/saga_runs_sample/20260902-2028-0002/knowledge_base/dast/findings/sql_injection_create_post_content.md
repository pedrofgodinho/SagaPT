## SQL Injection in POST /create_post — content field

- **Endpoint**: POST /create_post
- **Parameter**: content (form field)
- **Detection Payload**: `test'` (single quote appended)
- **Evidence**: Response contains visible MySQL error message:
  `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''test'') at line 1")`
- **HTTP Status**: 200 (with error displayed in page body)
- **Vulnerability Class**: Error-based SQL Injection
- **Priority**: High — visible SQL error messages directly confirm injectability