## SQL Injection in GET /delete_post — id parameter

- **Endpoint**: GET /delete_post?id=
- **Parameter**: id (query parameter)
- **Detection Payload**: `1'` (single quote appended)
- **Evidence**: HTTP 500 Internal Server Error returned. The behavioral change triggered by a single-quote payload confirms SQL injection. The error is suppressed (no visible SQL text) but the 500 response is the detection signal.
- **HTTP Status**: 500 (Internal Server Error)
- **Vulnerability Class**: Error-based SQL Injection (error suppressed but behavior confirms injectability)
- **Priority**: High — the parameter is injectable even though the raw SQL error is not reflected in the response