## SQL Injection in POST /signup — username field

- **Endpoint:** `POST /signup`
- **Parameter:** `username`
- **Detection payload:** `' OR 1=1 -- `
- **Evidence:** Submitting the SQLi payload in the username field with any name/password resulted in the application logging in as user `mr_robot` instead of creating a new account or showing a signup error. This authentication bypass behavior is consistent with SQL injection affecting the account creation or login logic.
- **Vulnerability class:** SQL Injection (authentication bypass)