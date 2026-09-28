# CORS Wildcard Access-Control-Allow-Origin

## Vulnerability Class
Cross-Origin Resource Sharing Misconfiguration

## Endpoint
All endpoints (confirmed on /rest/user/login, /api/Products, /api/SecurityQuestions, /api/Users, /ftp/, etc.)

## Description
Every response includes `Access-Control-Allow-Origin: *` (wildcard), allowing any website to make cross-origin requests to this application. This is confirmed by ZAP alert 10098 (Cross-Domain Misconfiguration).

## Evidence
- ZAP Alert: pluginId=10098, name="Cross-Domain Misconfiguration", risk="Medium", confidence="Medium"
- Header present on all tested responses including authenticated endpoints
- No `Access-Control-Allow-Credentials` restrictions observed

## Severity
**MEDIUM** - Enables cross-origin attacks from malicious sites.

## Impact
- Any malicious website can make authenticated requests to this API (if cookies/auth headers are included)
- Potential for CSRF-like attacks via CORS
- Data exfiltration from cross-origin requests