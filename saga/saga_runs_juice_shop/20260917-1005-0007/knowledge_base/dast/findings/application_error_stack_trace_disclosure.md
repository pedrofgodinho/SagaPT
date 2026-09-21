# Application Error Stack Trace Disclosure

## Vulnerability Class
Information Disclosure

## Endpoint
All REST API endpoints (`/rest/*`) and error paths

## Evidence
When requests are made to REST endpoints (which are intercepted by Angular's catch-all route), the server returns HTTP 500 with detailed stack traces:

```
<h1>OWASP Juice Shop (Express ^4.22.1)</h1>
<h2><em>500</em> Error: Unexpected path: /rest/...</h2>
<ul id="stacktrace">
  <li> at /juice-shop/build/routes/angular.js:18:18</li>
  <li> at /juice-shop/build/lib/utils.js:235:26</li>
  <li> at Layer.handle [as handle_request] (/juice-shop/node_modules/express/lib/router/layer.js:95)</li>
  <li> at trim_prefix (/juice-shop/node_modules/express/lib/router/index.js:328)</li>
  ...
</ul>
```

The stack trace reveals:
- Application path: `/juice-shop/`
- Express version: `Express ^4.22.1`
- Internal file paths: `/juice-shop/build/routes/angular.js`, `/juice-shop/build/lib/utils.js`, `/juice-shop/build/lib/insecurity.js`
- Node module paths

## Impact
Stack traces reveal internal file paths and application structure, aiding further reconnaissance and attack planning.