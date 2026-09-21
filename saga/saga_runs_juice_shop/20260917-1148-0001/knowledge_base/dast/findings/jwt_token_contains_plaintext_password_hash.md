## JWT Token Contains Plaintext Password Hash

**Endpoint:** POST /rest/user/login
**Vulnerability Class:** Sensitive Information Exposure

### Detection

The JWT token returned by the login endpoint contains the user's password hash in plaintext within the token payload.

### Evidence

Login response body:
```json
{
  "authentication": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJkYXRhIjp7ImlkIjoyNSwidXNlcm5hbWUiOiIiLCJlbWFpbCI6InJlY29uQHRlc3QuY29tIiwicGFzc3dvcmQiOiI0ODAzNDFhMGFhMjVhMGQ1Njk3YTYwNmQ0OTUxN2RmZCIsInJvbGUiOiJjdXN0b21lciIsImRlbHV4ZVRva2VuIjoiIiwibGFzdExvZ2luSXAiOiIwLjAuMC4wIiwicHJvZmlsZUltYWdlIjoiL2Fzc2V0cy9wdWJsaWMvaW1hZ2VzL3VwbG9hZHMvZGVmYXVsdC5zdmciLCJ0b3RwU2VjcmV0IjoiIiwiaXNBY3RpdmUiOnRydWUsImNyZWF0ZWRBdCI6IjIwMjYtMDktMTcgMTE6NTE6MzIuNDM5ICswMDowMCIsInVwZGF0ZWRBdCI6IjIwMjYtMDktMTcgMTE6NTE6MzIuNDM5ICswMDowMCIsImRlbGV0ZWRBdCI6bnVsbH0sImJpZCI6NiwiaWF0IjoxNzg5NjQ2NjIxfQ.cSvDD7zPg4wECPaK6a72v3iRoqfpMqiya740FgnJLfrR5dF3jnIE0YbZXchjYk8yU0rJgx4pqzidC552GqKvYGVeAoj8om313p_MzA9q0fLOFDmELTBMmxZyF20LDqJ3HSLbpx6WhBc_SUf4RVFOyl6R8g-dEWpEGXg_PxC4ENk",
    "bid": 6,
    "umail": "recon@test.com"
  }
}
```

Decoded JWT payload (middle segment):
```json
{
  "data": {
    "id": 25,
    "username": "",
    "email": "recon@test.com",
    "password": "480341a0aa25a0d5697a606d49517dfd",
    "role": "customer",
    "deluxeToken": "",
    "lastLoginIp": "0.0.0.0",
    "profileImage": "/assets/public/images/uploads/default.svg",
    "totpSecret": "",
    "isActive": true,
    "createdAt": "2026-09-17 11:51:32.439 +00:00",
    "updatedAt": "2026-09-17 11:51:32.439 +00:00",
    "deletedAt": null
  },
  "bid": 6,
  "iat": 1789646621
}
```

The `password` field contains the MD5 hash of the user's password (`480341a0aa25a0d5697a606d49517dfd` = MD5 of "TestPass123!").

### Impact

- Any party with access to the JWT token can obtain the user's password hash
- MD5 is a weak hashing algorithm susceptible to collision and rainbow table attacks
- Combined with the SQL injection vulnerability in the login endpoint, an attacker could potentially extract password hashes from the database as well

### Recommendation

- Do NOT include sensitive fields (password, password hash, secrets) in JWT tokens
- Use a minimal payload in JWT tokens (only non-sensitive claims like user ID, role, expiration)
- Store password hashes separately in the database and never transmit them

### JWT Algorithm

The token uses RS256 (RSA Signature with SHA-256) as indicated in the header: `{"typ":"JWT","alg":"RS256"}`