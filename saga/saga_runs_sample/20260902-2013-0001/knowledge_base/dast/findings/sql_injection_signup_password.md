## SQL Injection in POST /signup — password field

- **Endpoint:** `POST /signup`
- **Parameter:** `password`
- **Detection payload:** `' OR 1=1 -- `
- **Evidence:** Submitting the SQLi payload in the password field resulted in the application logging in as user `mr_robot` instead of creating a new account. This authentication bypass behavior is consistent with SQL injection in the password handling logic.
- **Vulnerability class:** SQL Injection (authentication bypass)