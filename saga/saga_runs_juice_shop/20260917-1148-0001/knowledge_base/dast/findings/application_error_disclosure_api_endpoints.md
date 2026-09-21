## Application Error Disclosure (Stack Trace) on Multiple API Endpoints

**Endpoints Affected:**
- GET /api/Order
- GET /api/Order/1
- GET /api/Order/2
- GET /api/Basket
- GET /api/Basket/1
- GET /api/Basket/2
- GET /api/Coupons
- GET /api/Coupons/1
- GET /api/Complaint
- GET /api/Complaint/1
- GET /api/Me
- GET /api/Feedback
- GET /api/Categories

**Vulnerability Class:** Sensitive Information Exposure

### Detection

All listed endpoints return HTTP 500 with a full server-side stack trace in the HTML response body when accessed without proper authentication or when the route is not recognized. The error message is "Error: Unexpected path: /api/XXX" followed by a detailed stack trace.

### Evidence

Request: `GET /api/Order` (unauthenticated)
Response: HTTP 500 with body containing:
```html
<h1>OWASP Juice Shop (Express ^4.22.1)</h1>
<h2><em>500</em> Error: Unexpected path: /api/Order</h2>
<ul id="stacktrace">
  <li>  at /juice-shop/build/routes/angular.js:18:18</li>
  <li>  at /juice-shop/build/lib/utils.js:235:26</li>
  <li>  at Layer.handle [as handle_request] (/juice-shop/node_modules/express/lib/router/layer.js:95:5)</li>
  <li>  at trim_prefix (/juice-shop/node_modules/express/lib/router/index.js:328:13)</li>
  <li>  at /juice-shop/node_modules/express/lib/router/index.js:286:9</li>
  <li>  at router.process_params (/juice-shop/node_modules/express/lib/router/index.js:346:12)</li>
  <li>  at next (/juice-shop/build/routes/verify.js:235:5)</li>
  <li>  at Layer.handle [as handle_request] (/juice-shop/node_modules/express/lib/router/layer.js:95:5)</li>
  <li>  at trim_prefix (/juice-shop/node_modules/express/lib/router/index.js:328:13)</li>
  <li>  at /juice-shop/node_modules/express/lib/router/index.js:286:9</li>
  <li>  at router.process_params (/juice-shop/node_modules/express/lib/router/index.js:346:12)</li>
  <li>  at next (/juice-shop/build/lib/insecurity.js:218:5)</li>
  <li>  at Layer.handle [as handle_request] (/juice-shop/node_modules/express/lib/router/layer.js:95:5)</li>
  <li>  at trim_prefix (/juice-shop/node_modules/express/lib/router/index.js:328:13)</li>
</ul>
```

### Impact

Stack traces reveal:
- Application framework: Express.js
- Application version: OWASP Juice Shop
- Exact file paths: `/juice-shop/build/routes/angular.js:18:18`, `/juice-shop/build/lib/utils.js:235:26`, `/juice-shop/build/lib/insecurity.js:218:5`
- Node.js module paths and line numbers in the application codebase
- Directory structure: `/juice-shop/build/` indicates a compiled/bundled Node.js application
- Custom middleware: `verify.js` and `insecurity.js` are referenced, indicating custom Express middleware

### Recommendation

Configure Express to suppress stack traces in production responses. Use a custom error handler middleware that returns generic error messages to clients while logging full details server-side.