# Application Error Disclosure

## Finding
The application exposes detailed error information including stack traces in HTTP 500 responses.

## Evidence
When accessing non-existent API endpoints, the application returns full stack traces:
```
Error: Unexpected path: /api/v1/users
  at /juice-shop/build/routes/angular.js:18:18
  at /juice-shop/build/lib/utils.js:235:26
  at Layer.handle [as handle_request] (/juice-shop/node_modules/express/lib/router/layer.js:95:5)
  at trim_prefix (/juice-shop/node_modules/express/lib/router/index.js:328:9)
  ...
```

## Affected Endpoints
- All `/api/v1/*` paths tested returned 500 with stack traces
- All `/rest/*` paths tested returned 500 with stack traces
- All non-existent `/api/{Resource}` paths returned 500 with stack traces

## Impact
- Reveals internal file paths and directory structure (`/juice-shop/build/routes/`)
- Exposes Express version and module structure
- Helps attackers map the application architecture
- Aids in identifying valid vs invalid endpoints

## Recommendation
Implement generic error handling that returns user-friendly error messages without stack traces in production.