## Vulnerability Class
Broken Access Control (Missing Authentication) - NOT PRESENT

## Endpoints Tested
- `GET /api/BasketItems` → 401 "UnauthorizedError: No Authorization header was found"
- `GET /api/Complaints` → 401 "UnauthorizedError: No Authorization header was found"
- `GET /api/Orders` → 500 "Error: Unexpected path: /api/Orders" (endpoint doesn't exist)
- `GET /api/Users/1` → 401 "UnauthorizedError: No Authorization header was found"
- `GET /api/Users/2` → 401 "UnauthorizedError: No Authorization header was found"
- `GET /api/Users/3` → 401 "UnauthorizedError: No Authorization header was found"

## Evidence
All authenticated endpoints return 401 Unauthorized when accessed without a valid JWT Bearer token. The application properly enforces authentication on:
- Basket items endpoint
- Complaints endpoint
- Users endpoint (by ID)
- The Orders endpoint does not exist at /api/Orders (returns 500)

## Conclusion
Unauthenticated access to authenticated endpoints is properly blocked. No broken access control vulnerability confirmed for unauthenticated access.

## Limitation
IDOR testing (accessing other users' data with valid auth) could not be completed because the scanning tools do not support custom Authorization: Bearer headers, and Juice Shop uses JWT tokens in the response body (not cookies). The login() tool returns 200 but sets 0 cookies, and subsequent requests still receive 401. A full IDOR assessment would require manual testing with the JWT token extracted from the login response.