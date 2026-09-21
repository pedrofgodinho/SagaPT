## Authentication Failure - REST Login Endpoint Returns 401

- **Endpoint:** POST /rest/user/login
- **Payload:** {"email": "admin@juice-sh.op", "password": "admin"} (and test@test.com/Test1234!)
- **Evidence:** All login attempts return 401 "Invalid email or password." regardless of credentials used.
- **Registration attempts:** POST /rest/user/registration and /rest/user/register both return 500 "Unexpected path"
- **Impact:** Cannot perform authenticated testing of protected API endpoints. The application may use a different authentication mechanism (e.g., ZAP forced user context, session cookies set externally).

- **Note:** The ZAP forced user context was configured by the recon agent (user_id: 256), but the login() function returns 200 with 0 cookies, suggesting authentication is managed externally.

- **Risk:** Medium - Prevents authenticated security testing