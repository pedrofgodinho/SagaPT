# Auth-Required Endpoint Leaks Stack Trace on 401

**Vulnerability Class:** Application Error Disclosure / Information Disclosure

**Affected Endpoints:**
- GET /api/SecurityAnswers
- GET /api/Feedbacks/{id} (individual feedback items)

**Detection Payload:**
```
GET /api/SecurityAnswers
```
(no Authorization header)

**Evidence:** Returns HTTP 401 with a stack trace in the HTML error page:
```
<title>UnauthorizedError: No Authorization header was found</title>
<ul id="stacktrace"></ul>
```

Similarly, individual feedback items (e.g., `/api/Feedbacks/1`) return 401 with identical stack trace HTML.

**Impact:**
- Confirms these endpoints require authentication
- The stack trace reveals Express.js internals even on authorization failures
- An attacker can use this to enumerate which endpoints exist vs. which don't (existing endpoints return 401 with stack trace; non-existent paths return 500 with full stack trace)

**Notes:**
- The public `/api/SecurityQuestions` endpoint (plural) is publicly accessible and returns all 14 questions - already recorded in existing finding
- This finding is for `/api/SecurityAnswers` (different endpoint, requires auth, leaks error details)