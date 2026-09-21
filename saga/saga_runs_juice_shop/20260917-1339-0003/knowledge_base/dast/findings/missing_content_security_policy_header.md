## Missing Content-Security-Policy Header

**Endpoint:** All endpoints (/, /rest/user/login, /api/Feedbacks/, /rest/web3/*, /ftp/*)
**Vulnerability Class:** Missing Security Header (defense-in-depth)

### Evidence
No `Content-Security-Policy` (CSP) header is present in any response.

ZAP Alert: "Content Security Policy (CSP) Header Not Set" (pluginId: 10038, Medium risk) on multiple endpoints including:
- POST /api/Feedbacks/
- POST /rest/web3/walletExploitAddress
- POST /rest/web3/walletNFTVerify
- POST /rest/web3/submitKey

Example response headers from GET /:
```
Access-Control-Allow-Origin: *
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Feature-Policy: payment 'self'
# NO Content-Security-Policy header
```

### Impact
Without CSP, the application has no browser-enforced restrictions on:
- Loading scripts from external origins (potential XSS payload delivery)
- Inline script execution
- Form action destinations (potential data exfiltration)
- Frame embedding

This significantly increases the impact of any XSS vulnerability that may exist in the Angular SPA's client-side code.

### Note
The application is an Angular SPA that loads all JavaScript from local files (main.js, scripts.js, polyfills.js). While this reduces the risk of external script injection, CSP would still protect against:
- Inline event handlers
- eval() usage
- Data URI script loading
- XSS from DOM-based vectors

### Remediation
Implement a strict CSP header:
```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com; connect-src 'self'; frame-ancestors 'self'
```