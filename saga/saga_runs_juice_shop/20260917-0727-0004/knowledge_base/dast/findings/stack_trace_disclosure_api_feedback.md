# Stack Trace Disclosure on /api/Feedback

**Endpoint:** GET /api/Feedback
**Vulnerability Class:** Information Disclosure (Stack Trace)
**Risk:** Medium

## Description
The unauthenticated GET request to `/api/Feedback` returns an HTTP 500 error with a full Express.js stack trace in the response body. The stack trace reveals internal file paths and server architecture details.

## Evidence
- **HTTP Status:** 500
- **Response Body:** HTML error page with title "Error: Unexpected path: /api/Feedback"
- **Stack Trace Exposes:**
  - Server path: `/juice-shop/build/routes/angular.js:18:18`
  - Server path: `/juice-shop/build/lib/utils.js:235:26`
  - Server path: `/juice-shop/build/routes/verify.js:235:5`
  - Server path: `/juice-shop/build/lib/insecurity.js:218:5`
  - Express version: Express ^4.22.1
  - Framework: Node.js with Express

## Impact
- Reveals the application's directory structure and file layout
- Discloses the web server framework and version (Express ^4.22.1)
- Provides internal file paths that could aid further reconnaissance
- The `/api/Feedback` endpoint is not implemented (dead endpoint)

## Remediation
- Return generic error messages to clients for unimplemented endpoints
- Log stack traces server-side only, not in HTTP responses
- Configure Express to suppress detailed error pages in production