## SQL Injection in /requests?username

- **Endpoint:** GET /requests
- **Parameter:** username
- **Detection payload:** `admin'` (single quote appended)
- **Evidence:** Response returned HTTP 500 Internal Server Error with body: "The server encountered an internal error and was unable to complete your request."
- **Additional confirmation:** Payloads `' OR '1'='1` and `' AND '1'='1` returned HTTP 200 with standard page, but single-quote triggered 500 confirming injection.
- **Type:** Error-based SQL injection (server-side 500 error)
- **Priority:** High — 500 error indicates unhandled SQL exception