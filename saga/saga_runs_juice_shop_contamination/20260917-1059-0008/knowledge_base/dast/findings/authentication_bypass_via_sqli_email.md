# Authentication Bypass via SQL Injection in Login Email Field

- **Endpoint:** POST /rest/user/login
- **Vulnerable Parameter:** email
- **Vulnerability Class:** Authentication Bypass via SQL Injection
- **Detection Payload:** `' OR '1'='1`
- **Evidence:** The payload `' OR '1'='1` in the email field returned HTTP 200 with a valid JWT Bearer token (same structure as the baseline login response), while the same request with a non-injecting value and wrong password returns 401. The SQL injection (confirmed in finding `sql_injection_login_email_field`) allows the attacker to bypass credential validation.
- **Payload:** `{"email": "' OR '1'='1", "password": "Test1234!"}`
- **Response:** HTTP 200 with JWT token in `authentication.token` field
- **Impact:** Attacker can log in as any user (or the first user in the database) without knowing valid credentials.
- **Priority:** High — direct authentication bypass.