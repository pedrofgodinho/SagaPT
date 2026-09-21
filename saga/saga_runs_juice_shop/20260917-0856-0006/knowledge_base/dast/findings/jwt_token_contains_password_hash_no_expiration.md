# JWT Token Contains Sensitive Data and No Expiration

## Vulnerability Class
Sensitive Data Exposure / Insecure Token Design

## Endpoint
`POST /rest/user/login`

## Evidence
The JWT token returned upon successful authentication (via SQLi bypass `' OR 1=1 -- `) contains:

**Header:** `{"typ":"JWT","alg":"RS256"}`

**Payload decoded:**
```json
{
  "data": {
    "id": 1,
    "username": "",
    "email": "admin@juice-sh.op",
    "password": "0192023a7bbd73250516f069df18b500",
    "role": "admin",
    "deleteToken": "",
    "lastLoginIp": "",
    "profileImage": "assets/public/images/uploads/defaultAdmin.png",
    "totpSecret": "",
    "isActive": true,
    "createdAt": "2026-09-17 08:56:42.663 +00:00",
    "updatedAt": "2026-09-17 08:56:42.663 +00:00",
    "deletedAt": null
  },
  "bid": 1,
  "iat": 1789636373
}
```

**Key issues:**
1. **Password hash in payload:** The MD5 hash of the admin password (`0192023a7bbd73250516f069df18b500`) is stored in the JWT payload, visible to anyone who captures the token.
2. **No expiration claim:** Token has `iat` but no `exp` claim, meaning the token never expires.
3. **Full user object:** The entire user record is embedded in the token, violating the principle of least data in tokens.

## Impact
Any intercepted JWT token allows offline cracking of the password hash, and the token can be reused indefinitely.

## Risk
**High** — Password hash exposure + non-expiring token enables persistent account takeover.