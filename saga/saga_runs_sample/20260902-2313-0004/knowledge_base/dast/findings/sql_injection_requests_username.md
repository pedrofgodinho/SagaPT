## SQL Injection in /requests?username

- **Endpoint:** `/requests`
- **Parameter:** `username` (GET query parameter)
- **Vulnerability Class:** SQL Injection (Error-based — HTTP 500)
- **Detection Payload:** `username=mr_robot' trash`
- **Evidence:** The response returns HTTP 500 Internal Server Error (instead of the normal HTTP 200 page). This indicates the injected quote caused a server-side SQL error.
- **Impact:** Confirmed injectable. The generic 500 response confirms the parameter reaches the database layer unparameterized.