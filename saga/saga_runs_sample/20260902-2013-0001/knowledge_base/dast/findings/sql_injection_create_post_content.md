## SQL Injection in POST /create_post — content field

- **Endpoint:** `POST /create_post`
- **Parameter:** `content`
- **Detection payload:** `' OR 1=1 -- `
- **Evidence:** Response returned a MySQL error: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '' at line 1")`. This is a clear SQL syntax error caused by the unescaped single quote in the payload.
- **Vulnerability class:** SQL Injection (MySQL syntax error)