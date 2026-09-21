## Login Password Field - Not SQLi Vulnerable

- **Endpoint:** POST /rest/user/login
- **Parameter:** password
- **Payloads Tested:** `' trash`, `'' OR '''`
- **Evidence:** Both payloads returned 401 "Invalid email or password." — the normal response for incorrect credentials. No 500 error or SQL error was triggered.
- **Assessment:** The password field appears to be properly parameterized or sanitized. No SQL injection vulnerability detected.