## SQL Injection in /direct_messages?username

- **Endpoint:** GET /direct_messages
- **Parameter:** username
- **Detection payload:** `admin'` (single quote appended)
- **Evidence:** Response returned HTTP 500 Internal Server Error with body: "The server encountered an internal error and was unable to complete your request."
- **Additional confirmation:** Payload `admin"` (double quote) also returned HTTP 500, confirming the error is triggered by quote injection.
- **Type:** Error-based SQL injection (server-side 500 error)
- **Priority:** High — 500 error indicates unhandled SQL exception