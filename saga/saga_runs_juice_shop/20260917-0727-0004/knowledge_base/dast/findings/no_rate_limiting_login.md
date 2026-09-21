## No Rate Limiting on Login Endpoint

**Endpoint:** POST /rest/user/login
**Vulnerability Class:** Brute Force Susceptibility

### Evidence
Tested 8 consecutive login attempts with wrong passwords for the same account:
- Attempts 1-5: ReconPass123! → wrongpass1 through wrongpass5
- Attempts 6-8: admin, password, 123456

All attempts returned identical 401 responses with body "Invalid email or password."
- No CAPTCHA introduced
- No account lockout
- No increasing delay between responses
- No rate-limit headers in responses

### Impact
An attacker can perform unlimited brute force attacks against user accounts without detection or throttling. Combined with the SQLi in the email field, this makes credential stuffing trivially easy.