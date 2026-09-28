## JWT Token Analysis

**Endpoint:** POST /rest/user/login (obtained via SQLi bypass)
**Vulnerability Class:** Information Disclosure / Token Configuration

### Token Structure
- **Algorithm:** RS256 (asymmetric RSA) — confirmed from JWT header `{"typ":"JWT","alg":"RS256"}`
- **Format:** Standard 3-part JWT (header.payload.signature)

### Decoded JWT Payload Claims
```json
{
  "data": {
    "id": 1,
    "username": "",
    "email": "admin@juice-sh.op",
    "password": "0192023a7bbd73250516f069df18b500",
    "role": "admin",
    "deluxeToken": "",
    "lastLoginIp": "",
    "profileImage": "assets/public/images/uploads/defaultAdmin.png",
    "topSecret": "",
    "isActive": true,
    "createdAt": "2026-09-17 08:11:58.031 +00:00",
    "updatedAt": "2026-09-17 08:11:58.031 +00:00",
    "deletedAt": null
  },
  "bid": 1,
  "iat": 1789633937
}
```

### Evidence
- Token obtained via SQLi bypass payload `' OR '1'='1' -- ` on login endpoint
- RS256 algorithm prevents simple algorithm confusion attacks (requires private key)
- Password hash exposed in JWT claims: `0192023a7bbd73250516f069df18b500`
- Full user profile data embedded in token including role, email, password hash
- Token contains `iat` (issued at) timestamp but **no `exp` (expiration) claim** — tokens may be valid indefinitely

### Analysis
The JWT uses RS256 which is secure against algorithm confusion attacks, but the token contains excessive sensitive data (password hash, full user profile). The absence of an expiration claim (`exp`) means tokens never expire.

### Impact
- Password hashes exposed in JWT tokens
- Tokens may never expire if not invalidated server-side
- Excessive data in token increases attack surface