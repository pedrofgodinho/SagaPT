## Missing Content Security Policy (CSP) Header

- **Endpoint:** All endpoints (confirmed on /, /rest/user/login, /rest/user/registration, /ftp/, /ftp/quarantine/)
- **Vulnerability Class:** Security Misconfiguration
- **Evidence:** HTTP responses across all tested endpoints lack the `Content-Security-Policy` header. ZAP alert "Content Security Policy (CSP) Header Not Set" fired with High confidence on multiple endpoints.
- **Impact:** Without CSP, the application is more susceptible to XSS attacks, data injection, and other code injection attacks. Browsers cannot enforce restrictions on which resources can be loaded or executed.
- **Priority:** MEDIUM