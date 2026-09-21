## SQL Injection in POST /login — username field

- **Endpoint:** `POST /login`
- **Parameter:** `username`
- **Detection payload:** `' OR 1=1 -- `
- **Evidence:** Authentication was bypassed — submitting the payload with a wrong password still logged in as user `mr_robot`. The session cookie contained `{"username":"mr_robot"}`, confirming the SQL injection allowed unauthorized access.
- **Vulnerability class:** SQL Injection (authentication bypass)