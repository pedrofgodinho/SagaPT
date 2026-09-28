# Missing Content-Security-Policy Header

## Vulnerability Class
Security Misconfiguration

## Endpoint
All endpoints (confirmed on /rest/user/login, /api/Products, /api/SecurityQuestions, /api/Users, /ftp/, etc.)

## Description
No `Content-Security-Policy` (CSP) header is present in any response. ZAP Alert 10038 (Content Security Policy (CSP) Header Not Set) triggered with High confidence.

## Evidence
- ZAP Alert: pluginId=10038, name="Content Security Policy (CSP) Header Not Set", risk="Medium", confidence="High"
- All tested responses lack the CSP header
- Other security headers present: X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Feature-Policy

## Severity
**MEDIUM** - Without CSP, the application is more vulnerable to XSS attacks.

## Impact
- No browser-level restriction on script sources, making XSS exploitation easier
- Combined with wildcard CORS, increases cross-origin attack surface
- Does not prevent XSS on its own but is an important defense-in-depth control