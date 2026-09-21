## No Email Enumeration via Login Endpoint

**Endpoint:** POST /rest/user/login
**Vulnerability Class:** Information Disclosure - Email Enumeration - NOT CONFIRMED

### Tests Performed
1. **Non-existent email:** `{"email": "nonexistent_user_12345@test.com", "password": "anyPassword"}`
   - Response: 401, body: "Invalid email or password.", Content-Length: 26, ETag: W/"1a-ARJvVK+smzAF3QQve2mDSG+3Eus"

2. **Existing email (wrong password):** `{"email": "test@test.com", "password": "wrongPassword123"}`
   - Response: 401, body: "Invalid email or password.", Content-Length: 26, ETag: W/"1a-ARJvVK+smzAF3QQve2mDSG+3Eus"

### Analysis
Both responses are byte-for-byte identical:
- Same HTTP status (401)
- Same response body ("Invalid email or password.")
- Same Content-Length (26)
- Same ETag value
- No timing difference observed

### Conclusion
The login endpoint does NOT reveal whether an email address is registered. It uses a generic error message for both invalid emails and wrong passwords, preventing email enumeration attacks.