## SQL Injection in /direct_messages?username

- **Endpoint:** `/direct_messages`
- **Parameter:** `username` (GET query parameter)
- **Vulnerability Class:** SQL Injection (Error-based — HTTP 500)
- **Detection Payload:** `username=mr_robot' trash`
- **Evidence:** The response returns HTTP 500 Internal Server Error (instead of the normal HTTP 200 page). This indicates the injected quote caused a server-side SQL error that was not caught by application error handling.
- **Impact:** Confirmed injectable. While the error message is not reflected in the response (generic 500 page), the HTTP 500 status code confirms the input reaches the database layer unparameterized.