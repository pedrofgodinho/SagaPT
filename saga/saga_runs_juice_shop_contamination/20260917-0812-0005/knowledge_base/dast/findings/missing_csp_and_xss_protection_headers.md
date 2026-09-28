## Missing Content-Security-Policy and X-XSS-Protection Headers

**Endpoint:** All endpoints on http://juiceshop.local:3000
**Vulnerability Class:** Information Disclosure / Security Misconfiguration

### Testing Performed
Checked HTTP response headers on multiple endpoints:
- `GET /` → 200
- `GET /admin` → 200
- `GET /rest/user/login` → 500
- `GET /scripts.js` → 200
- `GET /main.js` → 200
- `GET /polyfills.js` → 200
- `GET /styles.css` → 200
- `GET /robots.txt` → 200
- `GET /sitemap.xml` → 200
- `GET /?redirect=http://evil.com` → 200
- `GET /?return=http://evil.com` → 200
- `GET /?next=http://evil.com` → 200
- `GET /?url=http://evil.com` → 200

### Present Headers (consistent across all endpoints)
- `X-Content-Type-Options: nosniff` ✅
- `X-Frame-Options: SAMEORIGIN` ✅
- `Access-Control-Allow-Origin: *` (CORS wildcard - already confirmed)
- `Feature-Policy: payment 'self'`
- `X-Recruiting: /#/jobs` (information disclosure)

### Missing Headers
- **Content-Security-Policy** - NOT PRESENT on any endpoint
- **X-XSS-Protection** - NOT PRESENT on any endpoint

### Evidence
All tested endpoints return identical header sets without CSP or X-XSS-Protection. ZAP flagged "Content Security Policy (CSP) Header Not Set" (Medium risk, High confidence) and "Cross-Domain Misconfiguration" (Medium risk) on all requests.

### Impact
- Without CSP, the application has no defense against XSS attacks that may bypass other controls
- Without X-XSS-Protection, older browsers lack built-in XSS filtering
- Combined with the existing CORS wildcard, this increases the attack surface for reflected XSS attacks

### Mitigation
- Add `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';` (or more restrictive)
- Add `X-XSS-Protection: 1; mode=block`