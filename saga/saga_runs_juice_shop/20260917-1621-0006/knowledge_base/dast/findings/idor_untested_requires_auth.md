## IDOR Testing — Cannot Test Without Authentication

**Endpoint:** /api/Products/{id}, /api/SecurityQuestions/{id}, /api/Users/*
**Vulnerability Class:** Broken Access Control / IDOR
**Status:** Cannot confirm or rule out — requires authentication

### Tests Performed (Unauthenticated)
- `GET /api/Products/{id}` for various IDs (1, 2, 3, ..., 36, 999999, 1') → Valid IDs return product data, invalid IDs return 404
- `GET /api/SecurityQuestions/{id}` → 401 Unauthorized (requires JWT)
- `GET /api/Products?name=<xss_payload>` → Filters but no reflection

### Limitation
The login/signup POST endpoints (/rest/user/login, /rest/user/signup) are not directly accessible through the DAST scanning tools (they returned 500 "Unexpected path" errors). Without the ability to register a user or log in, IDOR testing on authenticated endpoints cannot be performed.

### Recommendations for Further Testing
1. Register a test user via the application's signup flow
2. Obtain a JWT token and use it in Authorization headers
3. Test IDOR on endpoints like /api/Products/{id} (accessing other users' data), /api/Basket, /api/Order, /api/Users/{id}
4. Test vertical escalation (low-privilege user accessing admin endpoints)

### Note
The /api/Products endpoint with numeric IDs returns 404 for non-existent IDs (e.g., 999999), suggesting the ID parameter is used in a direct lookup rather than a query that would be susceptible to IDOR without auth.