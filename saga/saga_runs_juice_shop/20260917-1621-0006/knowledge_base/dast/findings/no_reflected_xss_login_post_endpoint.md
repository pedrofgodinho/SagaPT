## No Reflected XSS on Login POST Endpoint

**Endpoint:** POST /rest/user/login
**Parameter:** email
**Vulnerability Class:** Reflected XSS (not confirmed)

### Tests Performed
- `POST /rest/user/login` with `{"email": "<script>alert(1)</script>", "password": "test"}` → 401 "Invalid email or password."
- `POST /rest/user/login` with `{"email": "<img src=x onerror=alert(1)>", "password": "test"}` → 401 "Invalid email or password."

### Evidence
Both XSS payloads returned the exact same response body (26 bytes): `Invalid email or password.` No user input is reflected in the error message.

### Conclusion
No reflected XSS vulnerability confirmed on the login email parameter. The application returns a generic error message without reflecting user input.