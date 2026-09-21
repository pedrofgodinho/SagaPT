# No CSRF Protection on Login Endpoint

## Vulnerability Class
Cross-Site Request Forgery (CSRF)

## Endpoint
`POST /rest/user/login`

## Evidence
- POST request to `/rest/user/login` with `{"email":"csrf@test.com","password":"csrfpass"}` was sent without Origin or Referer headers
- Response was HTTP 401 "Invalid email or password" — the request reached the application logic
- No CSRF token was required or validated in the response
- ZAP identified this as an "Authentication Request" (plugin 10111)
- No `Set-Cookie` header with SameSite attribute was observed in responses

The login endpoint accepts authentication requests without any CSRF token validation or Origin/Referer checking.

## Impact
An attacker could craft a malicious page that submits a POST request to `/rest/user/login` on behalf of a victim. While the login endpoint itself is less commonly exploited for CSRF (since the attacker needs the victim's credentials), this indicates a lack of CSRF protection across all state-changing POST endpoints.

## Risk
Medium — State-changing POST endpoints lack CSRF protection.

## Recommendation
Implement CSRF tokens for all state-changing POST endpoints, or use SameSite cookie attributes and Origin/Referer validation.