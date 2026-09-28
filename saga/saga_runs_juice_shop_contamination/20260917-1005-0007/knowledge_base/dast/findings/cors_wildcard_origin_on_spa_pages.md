# CORS Wildcard Origin Misconfiguration

## Vulnerability Class
Security Misconfiguration

## Endpoint
All SPA pages and static assets

## Evidence
ZAP alert confirmed: `Cross-Domain Misconfiguration` (Plugin ID: 10098, Confidence: Medium, Risk: Medium)

All responses include: `Access-Control-Allow-Origin: *`

## Impact
Wildcard CORS allows any origin to make cross-origin requests to the application, potentially enabling CSRF-based attacks and data exfiltration from authenticated sessions.