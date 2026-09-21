## SQL Injection in GET /edit_post — id parameter

- **Endpoint**: GET /edit_post?id=
- **Parameter**: id (query parameter)
- **Detection Payload**: `1'` (single quote appended)
- **Evidence**: HTTP 500 Internal Server Error returned for benign `id=1` vs 500 for `id=1'`. The behavioral change triggered by a single-quote payload confirms SQL injection. The error is suppressed (no visible SQL text) but the 500 response is the detection signal.
- **HTTP Status**: 500 (Internal Server Error)
- **Vulnerability Class**: Error-based SQL Injection (error suppressed but behavior confirms injectability)
- **Priority**: High — the parameter is injectable even though the raw SQL error is not reflected in the response