# SQL Injection Testing on Authenticated Endpoints — Blocked by Middleware

## Scope
Tested SQL injection on the following authenticated endpoints of OWASP Juice Shop:
- `POST /api/Feedbacks` (parameters: `comment`, `captchaId`)
- `POST /api/Complaints` (parameter: `message`)
- `POST /api/BasketItems` (parameters: `productId`, `quantity`)

## Results

### 1. `POST /api/Feedbacks` — `comment` parameter
- **Payloads tested**: `' OR 1=1 --`, `' UNION SELECT NULL --`, `' trash` (bare quote)
- **Result**: All requests returned identical response: `401 "Wrong answer to CAPTCHA. Please try again."`
- **Analysis**: The captcha middleware intercepts all requests before they reach the SQL layer. No SQL query is executed, so SQL injection cannot be confirmed or denied on this parameter.

### 2. `POST /api/Feedbacks` — `captchaId` parameter
- **Payloads tested**: `' OR 1=1 --`, `' UNION SELECT NULL --`, `' trash`
- **Result**: All requests returned identical response: `401 "Wrong answer to CAPTCHA. Please try again."`
- **Analysis**: Same captcha middleware block. Additionally, omitting `captchaId` entirely produces a 500 Sequelize validation error (`WHERE parameter "captchaId" has invalid "undefined" value`), confirming the captcha validation runs before any SQL query.
- **Note**: The captcha system uses Sequelize ORM (Captcha model), which typically uses parameterized queries, reducing SQLi risk.

### 3. `POST /api/Complaints` — `message` parameter
- **Result**: `401 "UnauthorizedError: No Authorization header was found"`
- **Analysis**: The endpoint requires a `Authorization: Bearer <JWT>` header. The `http_post` tool does not support custom headers, and the `login()` function (which restores cookie-based sessions) returned 0 cookies. The JWT token is returned in the response body (not as a cookie), so it cannot be automatically attached to subsequent requests.

### 4. `POST /api/BasketItems` — `productId` and `quantity` parameters
- **Result**: `401 "UnauthorizedError: No Authorization header was found"`
- **Analysis**: Same auth header limitation as Complaints endpoint.

## Tooling Limitations
1. **No custom header support**: `http_get` and `http_post` tools cannot attach `Authorization: Bearer <JWT>` headers required by Complaints and BasketItems endpoints.
2. **Captcha middleware**: The Feedbacks endpoint's captcha validation blocks all requests before the SQL layer is reached, making SQLi testing impossible.
3. **JWT token in body**: The JWT token is returned in the JSON response body (not as an HttpOnly cookie), so the `login()` function cannot persist it for authenticated requests.

## Conclusion
**SQL injection could NOT be confirmed or denied on these authenticated endpoints** due to middleware blocks (captcha) and tooling limitations (no custom header support for JWT Bearer auth). The existing unauthenticated SQLi findings cover:
- `POST /rest/user/login` → `email` field (confirmed SQLi)
- `GET /rest/products/search?q=` → `q` parameter (confirmed SQLi)