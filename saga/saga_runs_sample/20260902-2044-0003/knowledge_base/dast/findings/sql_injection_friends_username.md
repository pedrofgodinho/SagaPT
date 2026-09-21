## SQL Injection in /friends username parameter

**Endpoint:** `GET /friends`
**Parameter:** `username` (query parameter)
**Vulnerability Class:** SQL Injection (Error-based)

### Detection Payload
```
GET /friends?username=admin'%20--
```

### Evidence
The response contained a visible MySQL error message:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'admin' --')' at line 1")
```

This error confirms that the `username` parameter value is being concatenated directly into a SQL query without proper parameterization, allowing an attacker to break out of the string context and inject arbitrary SQL.

### Additional Notes
- The `search` parameter on the same endpoint was tested with payloads `'`, `'%20trash`, and was NOT vulnerable (all responses identical to baseline).
- A tautology payload (`admin'%20AND%20'1'='1`) returned 200 with "No friends" — no structural change observable, but the error-based payload confirms injectability.
- The application also discloses the MySQL error format, which could be leveraged for error-based data extraction by the exploitation agent.