## Stored XSS via Content Submission Endpoints — Unable to Test Without Auth

**Endpoints Tested:**
- `POST /api/Complaints` — requires JWT Authorization header (401 without auth)
- `POST /api/Feedbacks` — requires `captchaId` parameter (500 error without it)

### Tests Performed
- `POST /api/Complaints` with `{"description": "<script>alert('XSS')</script>"}` → 401 UnauthorizedError: No Authorization header was found
- `POST /api/Feedbacks` with `{"message": "<script>alert('XSS')</script>"}` → 500 Error: WHERE parameter "captchaId" has invalid "undefined" value

### Evidence
The `/api/Complaints` endpoint enforces JWT authentication. The `/api/Feedbacks` endpoint requires a captchaId parameter for validation. The http_post tool does not support custom Authorization headers, preventing authenticated testing.

### Note
- A test user was successfully registered at `/api/users` (dast@test.com, ID 26) and a JWT token was obtained via `POST /rest/user/login`.
- The login() tool returned 200 but did not establish a session cookie or attach the JWT token to subsequent requests.
- Prior DAST findings confirm stored XSS exists in product descriptions (GET /api/Products returns unescaped HTML in description fields).

### Conclusion
Stored XSS on content submission endpoints could not be confirmed due to authentication requirements. The application uses JWT-based auth for these endpoints.