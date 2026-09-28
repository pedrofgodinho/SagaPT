## CORS Misconfiguration - Wide Open Access

**Vulnerability Class:** Cross-Origin Resource Sharing (CORS) Misconfiguration
**Endpoint:** All endpoints
**Evidence:**
- All responses include `Access-Control-Allow-Origin: *` header
- This allows any origin to make cross-origin requests to the application
- Confirmed across login, whoami, security questions, and products endpoints

**Risk:** Combined with other vulnerabilities (like SQLi), this allows cross-origin attacks from any malicious website. An attacker could craft a malicious page that makes authenticated requests to the application if the victim has an active session.