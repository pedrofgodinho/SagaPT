# Stored XSS in Registration Endpoint - securityAnswer Field

- **Vulnerability Class**: Stored Cross-Site Scripting (XSS)
- **Endpoint**: `POST /api/Users`
- **Vulnerable Parameter**: `securityAnswer`
- **Detection Payload**: `<script>alert('stored XSS')</script>`
- **Evidence**: The payload was successfully stored in the database when registering a new user (HTTP 201 response). The `securityAnswer` field accepts and stores arbitrary HTML/script content without sanitization. The stored data can be retrieved via `GET /api/Users/{id}` when authenticated.
- **Response**: HTTP 201 with user created, payload stored in `securityAnswer` field
- **Impact**: When the security answer is displayed in the application (e.g., during account recovery, password reset, or admin review), the stored script will execute in the viewer's browser.
- **Note**: The application has no Content-Security-Policy header set, which would otherwise help mitigate XSS impact.