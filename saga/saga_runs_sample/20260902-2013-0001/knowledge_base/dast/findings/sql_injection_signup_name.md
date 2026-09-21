## SQL Injection in POST /signup — name field

- **Endpoint:** `POST /signup`
- **Parameter:** `name`
- **Detection payload:** `' OR 1=1 -- `
- **Evidence:** Submitting the SQLi payload in the name field with a valid username/password resulted in the application logging in as user `mr_robot` instead of creating a new account. This behavior indicates the payload altered the SQL query used during signup/login logic.
- **Vulnerability class:** SQL Injection