# Missing Content-Security-Policy Header

## Vulnerability Class
Security Misconfiguration

## Endpoint
All SPA pages and static assets

## Evidence
ZAP alert confirmed: `Content Security Policy (CSP) Header Not Set` (Plugin ID: 10038, Confidence: High, Risk: Medium)

No `Content-Security-Policy` header is present in any response from the Angular SPA.

## Impact
Without CSP, the application is more vulnerable to XSS attacks as browsers cannot enforce restrictions on script execution, content loading, or other security policies.