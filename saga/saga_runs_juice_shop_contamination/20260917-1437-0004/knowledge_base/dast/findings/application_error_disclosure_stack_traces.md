# Application Error Disclosure via Stack Traces

**Vulnerability Class:** Application Error Disclosure

**Affected Endpoints:** All non-existent API paths tested returned 500 errors with full Express/Node.js stack traces:
- GET /api/Me
- GET /api/Comments
- GET /api/Coupons
- GET /api/Countries
- GET /api/Deliveries
- GET /api/Disputed
- GET /api/Employees
- GET /api/Liabilities
- GET /api/PrivacyPolicies
- GET /api/Refunds
- GET /api/Roles
- GET /api/Salaries
- GET /api/Satisfactory
- GET /api/SecureFiles
- GET /api/SecurityAnswers (401 with stack trace)
- POST /rest/user/signup
- POST /rest/user/validateRegistrationToken
- POST /rest/user/confirmRegistrationToken
- POST /rest/user/resetPassword
- POST /rest/user/changePassword

**Detection Payload:** Any GET request to a non-existent API path, e.g.:
```
GET /api/Me
```

**Evidence:** Response returns HTTP 500 with full stack trace in body:
```
<title>Error: Unexpected path: /api/Me</title>
<ul id="stacktrace">
  <li> &nbsp; &nbsp;at /juice-shop/build/routes/angular.js:18:18</li>
  <li> &nbsp; &nbsp;at /juice-shop/build/lib/utils.js:235:26</li>
  <li> &nbsp; &nbsp;at Layer.handle [as handle_request] (/juice-shop/node_modules/express/lib/router/layer.js:95:5)</li>
  ...
</ul>
```

The stack trace reveals:
- Absolute filesystem paths to application source files (`/juice-shop/build/routes/angular.js`, `/juice-shop/build/lib/utils.js`)
- Express.js version and internal module paths
- Full call stack showing the request routing through verify.js, insecurity.js middleware

For auth-required endpoints (e.g., /api/SecurityAnswers), a 401 response also includes a stack trace:
```
<title>UnauthorizedError: No Authorization header was found</title>
<ul id="stacktrace"></ul>
```

**Impact:**
- Reveals internal application file structure and directory layout
- Exposes the technology stack (Express ^4.22.1, Node.js)
- Provides attacker with filesystem paths useful for path traversal or source code disclosure attacks
- Helps identify entry points for further enumeration

**Notes:**
- This is a consistent behavior across all unregistered endpoints
- The stack trace is returned even for 401 Unauthorized responses
- This differs from the existing "Application Error Disclosure" finding which was noted at Low risk - this confirms it is systemic across all error paths