## Application Error Disclosure via Stack Traces

**Endpoint:** Any non-existent API endpoint (e.g., /api/Feedback, /api/auth/login, /rest/user/signup, /api/v1/*)
**Vulnerability Class:** Information Disclosure
**HTTP Status:** 500 Internal Server Error

### Evidence
When accessing non-existent or invalid API endpoints, the application returns full stack traces including:
- Internal file paths: `/juice-shop/build/routes/fileServer.js:68:18`
- Internal file paths: `/juice-shop/build/lib/utils.js:235:26`
- Internal file paths: `/juice-shop/build/lib/insecurity.js:218:5`
- Internal file paths: `/juice-shop/build/lib/antiCheat.js:100:5`
- Express version: `Express ^4.22.1`
- Node.js module structure

### Example Responses
- `POST /api/Feedback` → 500: "Error: Unexpected path: /api/Feedback" with stack trace
- `POST /api/auth/login` → 500: "Error: Unexpected path: /api/auth/login" with stack trace
- `POST /rest/user/signup` → 500: "Error: Unexpected path: /rest/user/signup" with stack trace
- `GET /api/SecurityQuestions/1'` → 401: "UnauthorizedError: No Authorization header was found"

### Impact
- Reveals internal directory structure (`/juice-shop/build/routes/`, `/juice-shop/build/lib/`)
- Exposes Express version and module dependencies
- Helps attackers map application architecture
- Aids in identifying valid vs invalid endpoints
- Could reveal sensitive internal file names and code structure

### Recommendation
Implement generic error handling that returns user-friendly error messages without stack traces in production.