## Endpoint Mapping - API Route Discovery Results

### Working Endpoints (200 OK, unauthenticated):
- GET /api/Feedbacks - Returns all feedback entries
- GET /api/Challenges - Returns all challenge definitions
- GET /api/SecurityQuestions - Returns all security questions
- GET /api/products - Returns all products
- GET /api/products/1 - Returns single product

### Auth Required Endpoints (401):
- GET /api/Users - "UnauthorizedError: No Authorization header was found"
- GET /api/PrivacyRequests - "UnauthorizedError: No Authorization header was found"

### Non-existent Routes (500 "Unexpected path"):
- GET /api/orders
- GET /api/advertisements
- GET /api/recyclers
- POST /rest/user/registration
- POST /rest/user/register

### Error Disclosure:
- All 500 errors return full stack traces showing Express/Sequelize/SQLite internals
- Stack traces reveal file paths: /juice-shop/build/routes/angular.js, /juice-shop/node_modules/sequelize/
- This is already covered by existing finding "information_disclosure_stack_traces.md"

### Auth Mechanism:
- API uses Bearer token authentication (Authorization header required)
- REST login endpoint (/rest/user/login) does not appear functional
- ZAP forced user context may be managing session externally