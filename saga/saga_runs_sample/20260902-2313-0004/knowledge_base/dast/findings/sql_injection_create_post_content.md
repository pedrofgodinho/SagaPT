## SQL Injection in /create_post POST — content parameter

- **Endpoint:** POST /create_post
- **Parameter:** content
- **Vulnerability Class:** SQL Injection (error-based)
- **Detection Payload:** `' trash`
- **Evidence:** Response contains MySQL error: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash')' at line 1")`
- **Risk:** High — visible SQL error confirms the content parameter is concatenated into a SQL query without parameterization.