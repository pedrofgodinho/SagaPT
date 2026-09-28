## No Rate Limiting on Login Endpoint

**Endpoint:** POST /rest/user/login
**Vulnerability Class:** Missing Rate Limiting / Brute Force Susceptibility

### Testing Performed
Sent 5 consecutive login attempts with different email addresses and incorrect passwords in rapid succession (within ~3 seconds):
- test1@test.com / wrong
- test2@test.com / wrong
- test3@test.com / wrong
- test4@test.com / wrong
- test5@test.com / wrong

### Results
All 5 requests returned identical HTTP 401 responses with body "Invalid email or password." No throttling, delay, CAPTCHA, or account lockout was observed.

### Impact
An attacker can perform unrestricted brute force attacks against user credentials. Combined with the SQL injection vulnerability in the email field, this significantly lowers the barrier to unauthorized access.

### Notes
- The application does not implement any form of login rate limiting at the API level.
- No `Retry-After` header or similar mechanism was present in responses.