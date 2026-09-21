## No User Enumeration on Login Endpoint

**Endpoint:** POST /rest/user/login
**Vulnerability Class:** Information Disclosure / User Enumeration Resistance

### Testing Performed
Compared responses for valid vs invalid email addresses with incorrect passwords:

1. **Valid email, wrong password:**
   - Email: `admin@juice-sh.op`
   - Response: HTTP 401, body "Invalid email or password.", Content-Length: 26

2. **Invalid email, wrong password:**
   - Email: `nonexistent_user_12345@juice-sh.op`
   - Response: HTTP 401, body "Invalid email or password.", Content-Length: 26

### Results
Both responses are byte-identical. The application uses a generic error message that does not distinguish between "email not found" and "password incorrect."

### Impact
This is a **positive finding** — the application correctly prevents user enumeration by not revealing whether an email address is registered. This is a security best practice.

### Notes
- No timing differences were observed between valid and invalid email responses.
- No difference in response headers, status codes, or body length.