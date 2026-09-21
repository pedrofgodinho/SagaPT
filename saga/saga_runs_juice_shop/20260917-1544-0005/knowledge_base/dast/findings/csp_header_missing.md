## Content Security Policy Header Not Set

**Vulnerability Class:** Missing Security Header
**Endpoint:** All endpoints
**Evidence:**
- ZAP alert: "Content Security Policy (CSP) Header Not Set" detected on POST /rest/user/login
- No Content-Security-Policy header present in any response
- The application does not restrict which scripts/sources can execute

**Risk:** Without CSP, the application is more vulnerable to XSS attacks as there are no browser-enforced restrictions on script execution sources.