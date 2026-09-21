# Missing Content Security Policy (CSP) Header

**Endpoints:** All tested endpoints
**Vulnerability Class:** Security Misconfiguration

## Evidence
No `Content-Security-Policy` header is present in any response. ZAP flagged this as a Medium risk "Content Security Policy (CSP) Header Not Set" on multiple endpoints.

## Detection
```
GET /rest/web3/nftMintListen
Response Headers (no CSP):
  Access-Control-Allow-Origin: *
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Feature-Policy: payment 'self'
  X-Recruiting: /#/jobs
  Content-Type: application/json; charset=utf-8
```

## Impact
- No protection against XSS attacks via inline scripts
- No restriction on resource loading sources
- No protection against clickjacking beyond X-Frame-Options
- Angular SPA applications are particularly vulnerable without CSP

## Notes
The application does set `X-Content-Type-Options: nosniff` and `X-Frame-Options: SAMEORIGIN`, but CSP would provide defense-in-depth against XSS.