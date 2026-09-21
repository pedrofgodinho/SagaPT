## SQL Injection in POST /settings — bio field

- **Endpoint**: POST /settings
- **Parameter**: bio (form field)
- **Detection Payload**: `test'` (single quote appended)
- **Evidence**: Response contains visible MySQL error message:
  `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'mrrobot.png' WHERE username = 'mr_robot'' at line 1")`
- **HTTP Status**: 200 (with error displayed in page body)
- **Vulnerability Class**: Error-based SQL Injection
- **Priority**: High — visible SQL error messages directly confirm injectability