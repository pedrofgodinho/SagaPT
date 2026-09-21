# JWT Token Contains Plaintext Password Hash

## Vulnerability Class
Information Disclosure / Weak Token Design

## Endpoint
- POST http://juiceshop.local:3000/rest/user/login

## Description
The JWT authentication token returned by the login endpoint contains the user's password hash in plaintext within the JWT payload. The token uses RS256 (asymmetric, strong algorithm), but the payload design exposes sensitive data.

## Evidence
- JWT payload (decoded base64) contains: `"password":"480341a0aa25a0d5697a606d49517dfd"`
- This is a plaintext MD5 hash of the user's password
- The JWT header shows: `{"typ":"JWT","alg":"RS256"}`
- Token structure: `eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJkYXRhIjp7ImlkIjoyNSwidXNlcm5hbWUiOiJyZWNvbl90ZXN0X3VzZXIiLCJlbWFpbCI6InJlY29uQHRlc3QuY29tIiwicGFzc3dvcmQiOiI0ODAzNDFhMGFhMjVhMGQ1Njk3YTYwNmQ0OTUxN2RmZCIsInJvbGUiOiJjdXN0b21lciIsImRlbHV4ZVRva2VuIjoiIiwibGFzdExvZ2luSXAiOiIwLjAuMC4wIiwicHJvZmlsZUltYWdlIjoiL2Fzc2V0cy9wdWJsaWMvaW1hZ2VzL3VwbG9hZHMvZGVmYXVsdC5zdmciLCJ0b3RwU2VjcmV0IjoiIiwiaXNBY3RpdmUiOnRydWUsImNyZWF0ZWRBdCI6IjIwMjYtMDEtMDEgMDA6MDA6MDAuMDAwICswMDowMCIsInVwZGF0ZWRBdCI6IjIwMjYtMDktMTcgMDc6MDY6NTYuMDgzICswMDowMCIsImRlbGV0ZWRBdCI6bnVsbH0sImJpZCI6NiwiaWF0IjoxNzg5NjI5MTAzfQ.N9lbCbZpTDUkwUvaiLPme-l3sUMN-R4GAsrhJhzONbRzp9q2cWqpWujjc0TTGziy6fpajojwiEvL-u2doE0RUCvi6rLxUxdWDafci3RKUonoslsipvDuvZesAMqrmKlcKZF3PTz_cp-fRhqi0FC5Z32sp6tGZcB9AAinHVXmcwE`

## Severity
**MEDIUM** - Password hash in JWT enables offline cracking if token is intercepted.

## Impact
- If JWT token is intercepted, attacker can offline crack the MD5 hash
- MD5 is cryptographically broken for password hashing
- Token can be replayed if RS256 private key is compromised
- No expiration mechanism observed (no `exp` claim)