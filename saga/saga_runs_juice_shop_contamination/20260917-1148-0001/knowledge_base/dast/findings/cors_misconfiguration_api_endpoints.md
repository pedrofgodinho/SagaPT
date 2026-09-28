## CORS Misconfiguration — Access-Control-Allow-Origin: *

**Endpoints Affected:** All API endpoints tested
- GET /api/Users
- GET /api/Users/1
- GET /api/Users/25
- GET /api/Order
- GET /api/Basket
- GET /api/Coupons
- GET /api/Complaint
- GET /api/Me
- GET /api/Feedback
- GET /api/Categories
- GET /api/SecurityQuestions
- POST /api/Users (registration)
- POST /rest/user/login

**Vulnerability Class:** Cross-Domain Misconfiguration (CORS)

### Detection

All tested API endpoints include the header `Access-Control-Allow-Origin: *` in their responses, which allows any origin to make cross-origin requests to these endpoints.

### Evidence

Response headers from all endpoints include:
```
Access-Control-Allow-Origin: *
```

This was observed on responses from:
- `GET /api/Users` (401 response)
- `GET /api/Order` (500 response)
- `GET /api/SecurityQuestions` (200 response)
- `POST /rest/user/login` (200 response)
- `POST /api/Users` (201 response)

### Impact

- Any malicious website can make cross-origin requests to these API endpoints
- Combined with the login endpoint accepting credentials, a malicious site could potentially exfiltrate authentication tokens
- Attackers can use CORS misconfiguration to bypass same-origin policy and access sensitive API data from a victim's browser session
- If authenticated endpoints are accessed, the attacker could leverage the victim's session cookies/tokens

### Recommendation

Restrict `Access-Control-Allow-Origin` to specific trusted origins instead of using `*`. Implement a whitelist of allowed origins and validate the Origin header on each request.