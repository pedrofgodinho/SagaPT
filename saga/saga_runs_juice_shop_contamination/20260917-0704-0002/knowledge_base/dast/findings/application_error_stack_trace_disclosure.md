# Application Error Stack Trace Disclosure

## Vulnerability Class
Information Disclosure

## Endpoint
- GET/POST to non-existent or invalid API paths (e.g., `/api/Users/login`, `/api/User/login`, `/rest/user/me`, `/api/v1/users`)

## Description
The application returns detailed HTTP 500 error pages that include:
- Full application error messages (e.g., "Unexpected path: /api/Users/login")
- Complete server-side stack traces showing file paths and line numbers
- Internal framework structure paths (e.g., `/juice-shop/build/routes/angular.js:18:18`)
- Node.js module paths (e.g., `/juice-shop/node_modules/express/lib/router/layer.js:95`)

## Evidence
- POST to `/api/Users/login` → 500 with stack trace showing `/juice-shop/build/routes/angular.js:18:18`
- GET to `/rest/user/me` → 500 with stack trace showing `/juice-shop/build/lib/utils.js:235:26`
- GET to `/api/v1/users` → 500 with stack trace
- POST to `/api/Products/1'--%20` → 404 (no error leak, but path reveals structure)

## Severity
**LOW** - Stack traces reveal internal application structure.

## Impact
- Reveals application architecture (Angular routing layer, Express middleware chain)
- Exposes internal file paths and directory structure (`/juice-shop/build/`)
- May aid attackers in crafting targeted exploits
- ZAP Alert 90022 (Application Error Disclosure) triggered