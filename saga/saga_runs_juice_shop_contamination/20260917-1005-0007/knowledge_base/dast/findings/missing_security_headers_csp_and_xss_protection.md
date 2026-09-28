# Missing Security Headers: CSP and X-XSS-Protection

## Vulnerability Class
Information Disclosure / Security Misconfiguration

## Endpoint
All endpoints, verified on:
- `GET /` (home page)
- `GET /#/login`
- `GET /#/admin`
- `GET /#/product/1`
- `GET /ftp/acquisitions.md`

## Evidence
All responses were checked for security headers. The following headers are **present**:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Feature-Policy: payment 'self'`
- `X-Recruiting: /#/jobs`

The following critical security headers are **missing**:
- **Content-Security-Policy (CSP)**: Not set on any response
- **X-XSS-Protection**: Not set on any response

## Impact
Without CSP, the application has no defense against Cross-Site Scripting (XSS) attacks via browser-side enforcement. Without X-XSS-Protection, older browsers won't activate their built-in XSS filtering. These missing headers increase the attack surface for reflected and stored XSS attacks.

## Detection
Checked response headers on multiple endpoints - all lack `Content-Security-Policy` and `X-XSS-Protection` headers.