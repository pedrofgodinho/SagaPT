## Server Error Stack Traces in Error Responses

**Endpoints:** Multiple unimplemented routes return full stack traces
**Vulnerability Class:** Information Disclosure

### Evidence
All tested unimplemented endpoints return 500 errors with full Express.js stack traces:

1. **GET /rest/user/me** → 500 with stack trace revealing:
   - `/juice-shop/build/routes/angular.js:18:18`
   - `/juice-shop/build/lib/utils.js:235:26`
   - `/juice-shop/node_modules/express/lib/router/layer.js:95:5`
   - `/juice-shop/build/routes/verify.js:235:5`
   - `/juice-shop/build/lib/insecurity.js:218:5`

2. **GET /api/v1/users** → 500 with identical stack trace structure
3. **GET /api/v1/products** → 500 with identical stack trace structure
4. **POST /rest/feedback** → 500 with identical stack trace structure

### Server Version Disclosure
Error page header: `OWASP Juice Shop (Express ^4.22.1)`
- Application name: OWASP Juice Shop
- Framework version: Express ^4.22.1
- Full build paths disclosed: `/juice-shop/build/...`

### Impact
- Full server directory structure exposed
- Framework version disclosed for targeted attacks
- Node.js module paths revealed
- Internal application architecture exposed