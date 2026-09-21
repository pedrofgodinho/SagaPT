# Missing Security Headers

## Vulnerability Class
Security Misconfiguration

## Endpoint
All endpoints on http://juiceshop.local:3000

## Evidence
Every HTTP response was analyzed for security headers. The following headers are **missing**:

| Header | Present? |
|--------|----------|
| `Content-Security-Policy` | **MISSING** |
| `Strict-Transport-Security` (HSTS) | **MISSING** |
| `X-XSS-Protection` | **MISSING** |
| `Referrer-Policy` | **MISSING** |
| `Permissions-Policy` | **MISSING** |

The following security headers **are present**:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Feature-Policy: payment 'self'`

ZAP confirmed these findings with alerts:
- Plugin 10038: Content Security Policy (CSP) Header Not Set (High confidence, Medium risk)
- Missing HSTS and X-XSS-Protection confirmed on all tested endpoints

## Impact
- **No CSP**: Allows unrestricted script execution, facilitating XSS attacks
- **No HSTS**: Users can be downgraded to HTTP via man-in-the-middle attacks
- **No X-XSS-Protection**: Older browsers lack built-in XSS filtering
- **No Referrer-Policy**: Sensitive URL data may leak to third parties

## Risk
Medium — Multiple missing security headers reduce defense-in-depth.

## Recommendation
Implement Content-Security-Policy, Strict-Transport-Security, X-XSS-Protection, Referrer-Policy, and Permissions-Policy headers.