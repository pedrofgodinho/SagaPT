# CORS Wildcard Misconfiguration

## Vulnerability Class
Cross-Origin Resource Sharing (CORS) Misconfiguration

## Endpoint
All endpoints on http://juiceshop.local:3000

## Evidence
Every HTTP response includes the header:
```
Access-Control-Allow-Origin: *
```

This was confirmed on:
- GET /api/products (200)
- GET / (SPA shell, 200)
- GET /ftp/ (directory listing, 200)
- GET /api/products?q=<script>alert(1)</script> (200)
- All other tested endpoints

## Impact
Any malicious website can make cross-origin requests to this application, potentially reading sensitive data returned by the API. While the application does not appear to use credentials in cross-origin requests (no `Access-Control-Allow-Credentials: true`), the wildcard still represents a misconfiguration that could be exploited in combination with other vulnerabilities.

## Risk
Medium — Wildcard CORS enables cross-origin data access from any domain.