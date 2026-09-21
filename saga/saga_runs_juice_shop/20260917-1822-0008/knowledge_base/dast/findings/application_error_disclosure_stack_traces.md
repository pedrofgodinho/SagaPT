## Vulnerability: Application Error Disclosure via Stack Traces

**Endpoint:** Multiple invalid paths tested
**Parameter:** N/A (path-based)
**Vulnerability Class:** Information Disclosure

### Description
The application exposes detailed Express.js stack traces when accessing invalid or non-existent API paths. The error responses include:
- Full Express version (Express ^4.22.1)
- Internal file paths (e.g., `/juice-shop/build/routes/angular.js:18:18`)
- Complete call stack with file names and line numbers
- Node.js module paths (`/juice-shop/node_modules/express/lib/router/...`)

### Affected Endpoints (all return 500 with stack trace):
- `/api/User`, `/api/Memory`, `/api/Meta`, `/api/Recycling`, `/api/Address`, `/api/Delivery`
- `/rest/challenge`, `/rest/user/me`, `/rest/user/1`, `/rest/user/2`
- `/rest/address/1`, `/rest/order/1`, `/rest/payment/1`, `/rest/securityQuestion/1`
- `/rest/recycling/1`, `/rest/delivery/1`

### Evidence
Response body contains:
```
<h1>OWASP Juice Shop (Express ^4.22.1)</h1>
<h2><em>500</em> Error: Unexpected path: /api/User</h2>
<ul id="stacktrace"><li> &nbsp; &nbsp;at /juice-shop/build/routes/angular.js:18:18</li>...</ul>
```

### Impact
Stack traces reveal internal application structure, file paths, technology stack, and version information that aids attackers in crafting targeted exploits.

### Risk
Low - Information disclosure that aids reconnaissance.