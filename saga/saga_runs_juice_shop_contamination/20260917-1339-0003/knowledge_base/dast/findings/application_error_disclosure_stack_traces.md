## Application Error Disclosure via Stack Traces

**Endpoints:** POST /api/Feedbacks/, GET /api/Challenges/?sort=createdAt&sort=-createdAt, GET /api/Challenges/?sort=createdAt', GET /api/v1/orders/1, GET /api/v1/users/1, GET /rest/order/1, GET /api/files, GET /api/v1/files
**Vulnerability Class:** Information Disclosure (Application Error Disclosure)

### Detection Payloads

1. **POST /api/Feedbacks/** with minimal body:
   - Payload: `{"comment": "test", "rating": 5}`
   - Response: HTTP 500 with full stack trace
   - Evidence: `Error: WHERE parameter "captchaId" has invalid "undefined" value`
   - Stack trace references: `/juice-shop/node_modules/sequelize/lib/dialects/abstract/query-generator.js:1770`, `SQLiteQueryGenerator.whereItemQuery`, `Captcha.findAll`, `/juice-shop/build/routes/captcha.js:33`

2. **GET /api/Challenges/?sort=createdAt&sort=-createdAt**:
   - Response: HTTP 500 with `{"message":"internal error","errors":["sortQuery.split is not a function"]}`

3. **GET /api/Challenges/?sort=createdAt'** (SQL injection probe on sort):
   - Response: HTTP 400 with `{"message":"Sorting not allowed on given attributes","errors":["createdAt'"]}` — reveals the sort parameter is validated against a whitelist

4. **GET /api/v1/orders/1**, `/api/v1/users/1`, `/rest/order/1`, `/api/files`, `/api/v1/files`:
   - All return HTTP 500 with full Angular/Express stack traces
   - Evidence: `Error: Unexpected path: /api/v1/orders/1`
   - Stack trace references: `/juice-shop/build/routes/angular.js:18`, `/juice-shop/build/lib/utils.js:235`, `/juice-shop/build/routes/verify.js:235`, `/juice-shop/build/lib/insecurity.js:218`

5. **GET /api/Feedbacks/1** (unauthenticated individual access):
   - Response: HTTP 401 with `UnauthorizedError: No Authorization header was found`
   - Stack trace section is empty (`<ul id="stacktrace"></ul>`)

### Impact
Attackers can extract:
- Internal file paths on the server (`/juice-shop/node_modules/sequelize/...`, `/juice-shop/build/routes/...`)
- Database technology (SQLite) and ORM (Sequelize) details
- Internal module structure and route handler locations
- Parameter validation logic (e.g., sort whitelist)
- The application's security middleware chain (verify.js, insecurity.js)

### Notes
This is a development/debug configuration that should not be present in production. The stack traces reveal the full directory structure and technology stack.