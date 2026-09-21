## SQL Injection in POST /remove_request — username field

- **Endpoint:** `POST /remove_request`
- **Parameter:** `username`
- **Detection payload:** `' OR 1=1 -- `
- **Evidence:** Response returned a MySQL error: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '' at line 1")`. This confirms the username field is directly concatenated into a SQL query without parameterization.
- **Vulnerability class:** SQL Injection (MySQL syntax error)