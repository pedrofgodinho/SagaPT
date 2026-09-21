## Cross-Origin Resource Sharing (CORS) Wildcard (*)

- **Endpoint:** All endpoints (confirmed on /, /rest/user/login, /rest/user/registration, /ftp/, /ftp/quarantine/)
- **Vulnerability Class:** Security Misconfiguration
- **Evidence:** All HTTP responses include `Access-Control-Allow-Origin: *` header. ZAP alert "Cross-Domain Misconfiguration" fired with Medium confidence.
- **Impact:** Any website can make cross-origin requests to this application, including reading responses. Combined with authentication endpoints, this could allow malicious sites to read sensitive data or perform actions on behalf of authenticated users.
- **Priority:** MEDIUM