## Missing Content-Security-Policy Header

- **Endpoint:** All endpoints (confirmed on GET /, GET /ftp/acquisitions.md, GET /ftp/../../../etc/passwd, etc.)
- **Evidence:** No `Content-Security-Policy` header is present in any response. ZAP alert 10038 "Content Security Policy (CSP) Header Not Set" (High confidence) fired on multiple requests.
- **Impact:** Without CSP, the application is more vulnerable to XSS attacks, data injection, and other code injection attacks. The browser has no policy to restrict which sources scripts can be loaded from.
- **Risk:** Medium
