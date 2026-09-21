## SQL Injection in /signup POST — username parameter

- **Endpoint:** POST /signup
- **Parameter:** username
- **Vulnerability Class:** SQL Injection (error-based)
- **Detection Payload:** `' trash`
- **Evidence:** Response contains MySQL error: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash'' at line 1")`
- **Risk:** High — visible SQL error confirms the username parameter is concatenated into a SQL query without parameterization.