# JWT Uses RS256 Algorithm - Not Vulnerable to Algorithm "None" Attack

**Vulnerability Class:** JWT Security Configuration

**Affected Endpoints:**
- POST /rest/user/login (returns JWT token)

**Evidence:**
All JWT tokens returned by the login endpoint have the header:
```json
{"typ":"JWT","alg":"RS256"}
```

The RS256 algorithm uses RSA public-key cryptography:
- The token is signed with the server's private RSA key
- Verification uses the public RSA key
- Algorithm "none" attack is NOT possible because the server expects RS256 signatures
- Without the private RSA key, tokens cannot be forged regardless of algorithm manipulation

**JWT Token Structure Observed:**
```
Header: {"typ":"JWT","alg":"RS256"}
Payload: {"data":{"id":25,"username":"reconuser","email":"recon@test.com","role":"customer",...},"bid":7,"iat":1789658709}
Signature: RSA-SHA256 signature (valid)
```

**Impact:**
- JWT tokens are cryptographically signed with RS256, which is a strong algorithm
- Algorithm confusion attacks (switching to "none" or "HS256") are ineffective
- Token forgery would require obtaining the server's private RSA key
- The SQL injection authentication bypass (already confirmed) provides admin access without needing JWT forgery

**Notes:**
- RS256 is more secure than HS256 for multi-tenant applications as the public key can be shared without exposing the signing secret
- The application uses Sequelize/SQLite backend with RSA key-based JWT verification