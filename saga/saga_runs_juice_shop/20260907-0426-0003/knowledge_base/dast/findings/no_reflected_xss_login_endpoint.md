# No Reflected XSS in Login Endpoint

- **Vulnerability Class**: Reflected Cross-Site Scripting (XSS) - NOT PRESENT
- **Endpoint**: `POST /rest/user/login`
- **Parameters Tested**: `email`, `password`
- **Payloads Tested**:
  - `<script>alert('XSS')</script>` in both fields
- **Result**: No reflected XSS found. The login endpoint returns a generic 500 error HTML page that does not echo user input back into the response. The error page is a static Express error template.
- **Note**: The login endpoint is vulnerable to SQL injection (confirmed by separate DAST finding), but XSS is not present in the error response.