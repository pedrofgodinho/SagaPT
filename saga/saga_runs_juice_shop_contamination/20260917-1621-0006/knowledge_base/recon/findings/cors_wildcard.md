# Wildcard CORS Configuration

## Finding
The application returns `Access-Control-Allow-Origin: *` on all responses, enabling cross-origin requests from any domain.

## Evidence
All tested endpoints returned this header:
- GET / (main page)
- GET /api/Products
- GET /api/SecurityQuestions
- GET /api/Users
- GET /robots.txt
- All FTP endpoints

## Impact
- Allows any malicious website to make authenticated requests to this application on behalf of a logged-in user
- Combined with JWT auth, enables CSRF-like attacks via CORS
- No origin validation is performed

## Recommendation
Restrict CORS to specific trusted origins only.