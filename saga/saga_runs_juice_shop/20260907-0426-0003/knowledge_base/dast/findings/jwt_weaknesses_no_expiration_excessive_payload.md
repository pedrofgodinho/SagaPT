## JWT Weaknesses - No Expiration and Excessive Payload Data

**Vulnerability Class**: JWT Weaknesses
**Endpoint**: POST /rest/user/login

**Description**:
The JWT token returned on login contains several weaknesses:

1. **Missing Expiration (exp) Claim**: The JWT payload contains `iat` (issued at) but no `exp` (expiration) claim, meaning the token never expires and can be used indefinitely if compromised.

2. **Excessive Permissions/Data in Payload**: The JWT payload contains the entire user object including:
   - `id`: 25
   - `username`: ""
   - `email`: "test@test.com"
   - `password`: "912b7bc95fb9e6885a4685746433f39a" (password hash)
   - `role`: "customer"
   - `deluxeToken`: ""
   - `lastLoginIp`: "0.0.0.0"
   - `profileImage`: path
   - `topSecret`: ""
   - `isActive`: true
   - `createdAt`, `updatedAt` timestamps

3. **Password Hash in Token**: The JWT payload contains the hashed password, which is unnecessary and increases the impact if the token is intercepted.

**JWT Structure**:
- Header: `{"typ":"JWT","alg":"RS256"}`
- Algorithm: RS256 (asymmetric)
- Token returned in response body field `authentication.token`, not as HttpOnly cookie

**Evidence**:
- Captured JWT token from `POST /rest/user/login` with credentials test@test.com / testtest123
- Decoded payload shows all fields listed above
- No `exp` claim present

**Risk**: High - Tokens never expire, increasing window of exploitation. Password hash in token payload increases data exposure. RS256 signing means tampering requires private key, but token theft alone is sufficient for account takeover.