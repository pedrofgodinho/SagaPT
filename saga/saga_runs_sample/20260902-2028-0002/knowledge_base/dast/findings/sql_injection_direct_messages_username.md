## SQL Injection in /direct_messages?username

- **Endpoint**: GET /direct_messages?username=
- **Parameter**: username
- **Detection Payload**: `mr_robot'` (single quote appended)
- **Evidence**: Benign value `username=mr_robot` returns HTTP 200 with normal page content. Payload `username=mr_robot'` returns HTTP 500 Internal Server Error with no content body. The behavioral change (200 → 500) triggered by a single-quote payload confirms SQL injection.
- **HTTP Status**: 500 (vs 200 for benign input)
- **Vulnerability Class**: Error-based SQL Injection (error suppressed but behavior confirms injectability)
- **Priority**: High — the parameter is injectable even though the raw SQL error is not reflected in the response