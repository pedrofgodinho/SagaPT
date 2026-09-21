## SQL Injection in /direct_messages?username

- **Endpoint:** `GET http://www.hackergram.com/direct_messages?username=`
- **Parameter:** `username` (query string)
- **Detection payload:** `' trash`
- **Evidence:** Response is a `500 Internal Server Error`, indicating the single quote broke the underlying SQL query.
- **Response status:** 500 Internal Server Error
- **Severity:** High — the application crashes with a 500 error when the parameter is tampered with, confirming the parameter is not safely parameterized.