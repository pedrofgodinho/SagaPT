## CORS Misconfiguration - Wildcard Origin

- **Endpoint:** All endpoints (confirmed on GET /, GET /ftp/acquisitions.md, GET /rest/user/login, etc.)
- **Vulnerable Header:** `Access-Control-Allow-Origin: *`
- **Evidence:** Every response includes `Access-Control-Allow-Origin: *` header, allowing any origin to make cross-origin requests.
- **ZAP Alerts:** Plugin 10098 "Cross-Domain Misconfiguration" (Medium confidence) fired on multiple requests.
- **Impact:** Any malicious website can make cross-origin requests to this application, potentially reading sensitive data if authentication cookies are sent cross-origin. Combined with the lack of authentication enforcement on REST endpoints, this could enable data theft.
- **Risk:** Medium
