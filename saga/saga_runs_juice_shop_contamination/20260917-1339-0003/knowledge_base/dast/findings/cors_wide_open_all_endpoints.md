## CORS Misconfiguration - Wide Open

**Endpoint:** All endpoints (/, /rest/user/login, /api/Feedbacks/, /rest/web3/*, /ftp/*)
**Vulnerability Class:** Cross-Origin Resource Sharing (CORS) Misconfiguration

### Evidence
All tested endpoints return:
```
Access-Control-Allow-Origin: *
```

ZAP alerts confirmed "Cross-Domain Misconfiguration" (pluginId: 10098, Medium risk) on multiple endpoints including:
- GET /
- POST /rest/user/login
- POST /api/Feedbacks/
- POST /rest/web3/walletExploitAddress
- POST /rest/web3/walletNFTVerify
- POST /rest/web3/submitKey

### Impact
Any origin can make cross-origin requests to this application. While cookies are not sent by default in cross-origin requests (browsers block them unless `Access-Control-Allow-Credentials: true` is set), the wildcard origin means there is no whitelist enforcement. If credentials-based endpoints exist, they could be vulnerable to CSRF combined with CORS.

### Detection Payload
No special payload needed - simply making any request to the endpoint returns `Access-Control-Allow-Origin: *` in the response headers.

### Remediation
Restrict `Access-Control-Allow-Origin` to specific trusted origins. Remove the wildcard `*` and implement an allowlist of permitted origins.