# Angular Catch-All Route Blocks REST Endpoint Access

## Vulnerability Class
Application Architecture / Testing Limitation

## Endpoint
All REST API endpoints: `/rest/product/search`, `/rest/complaint`, `/rest/feedback`, `/rest/recycle`, and all other `/rest/*` paths

## Evidence
All requests to REST endpoints return HTTP 500 with the error:
```
Error: Unexpected path: /rest/...
```
Stack trace points to: `/juice-shop/build/routes/angular.js:18:18`

The Angular catch-all route intercepts all `/rest/*` requests before they reach the backend Express handlers. This prevents any direct HTTP probing of REST endpoints via this scanning tool.

## Tested Endpoints (all returned 500):
- `GET /rest/product/search?q=<script>alert(1)</script>` → 500
- `GET /rest/product/search?q=<img src=x onerror=alert(1)>` → 500
- `GET /rest/product/search?q=<svg/onload=alert(1)>` → 500
- `POST /rest/complaint` → 500
- `POST /rest/feedback` → 500
- `POST /rest/recycle` → 500

## Impact
XSS and other injection testing on REST endpoints cannot be performed using this tool because the Angular catch-all route intercepts all requests. The application error disclosure (stack trace) is visible in the 500 response body.