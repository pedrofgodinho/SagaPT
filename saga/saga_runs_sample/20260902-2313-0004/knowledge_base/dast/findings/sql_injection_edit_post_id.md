## SQL Injection in /edit_post?id=

- **Vulnerability class:** SQL Injection (Error-based)
- **Endpoint:** `GET /edit_post?id=`
- **Vulnerable parameter:** `id` (query string)
- **Detection payload:** `' trash`
- **Evidence:** Benign request `id=1` returns HTTP 200; injection payload `' trash` returns HTTP 500 Internal Server Error. The 500 response is consistent across all three probe payloads (`' trash`, `' OR '1'='1`, `' UNION SELECT NULL --`), confirming the parameter is concatenated into a SQL query without proper parameterization.
- **Risk:** High — attacker can alter SQL query structure, potentially reading/modifying/deleting data.