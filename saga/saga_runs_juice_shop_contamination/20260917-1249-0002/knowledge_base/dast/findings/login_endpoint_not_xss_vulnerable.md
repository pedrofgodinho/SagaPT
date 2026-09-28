## Login Endpoint - No Reflected XSS

- **Endpoint:** POST /rest/user/login
- **Parameters Tested:** email, password
- **Payloads Tested:** `<script>alert(1)</script>`
- **Evidence:** Both fields returned plain text response "Invalid email or password." with no HTML reflection. The login endpoint returns JSON/plain text, not HTML, so XSS is not applicable here.
- **Assessment:** No reflected XSS vulnerability on login endpoint.