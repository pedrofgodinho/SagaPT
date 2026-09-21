## SQL Injection in POST /login — password field

- **Endpoint:** `POST /login`
- **Parameter:** `password`
- **Detection payload:** `' OR '1'='1`
- **Evidence:** Authentication was bypassed — submitting the payload with the correct username `mr_robot` logged in successfully. The session cookie contained `{"username":"mr_robot"}`, confirming SQL injection in the password field allowed authentication bypass.
- **Vulnerability class:** SQL Injection (authentication bypass)