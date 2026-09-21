## SQL Injection in POST /request_friend - username field

- **Endpoint:** POST /request_friend
- **Parameter:** username
- **Detection payload:** `stark'` (single quote appended to username value)
- **Evidence:** Response returned HTTP 500 Internal Server Error with body: "The server encountered an internal error and was unable to complete your request."
- **Type:** Error-based SQL injection (server-side 500 error)
- **Priority:** High — 500 error indicates unhandled SQL exception