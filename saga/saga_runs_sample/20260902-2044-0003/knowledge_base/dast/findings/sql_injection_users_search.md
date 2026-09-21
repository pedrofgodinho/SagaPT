## SQL Injection in /users?search parameter

**Endpoint:** `GET http://www.hackergram.com/users?search=`
**Parameter:** `search` (query string)
**Vulnerability Class:** SQL Injection (MySQL)

### Detection Payload
```
'
```

### Evidence
Sending the bare single quote `'` as the `search` parameter value causes the application to return a visible MySQL error:

```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''' at line 1")
```

The response changes from a normal search results page (status 200, title "Hackergram - Search users") to an error page (status 200, title "Hackergram - Error") containing the raw SQL error message. ZAP also flagged this as "Application Error Disclosure" (plugin 90022, Medium confidence).

### Impact
The `search` parameter is concatenated into a SQL query without parameterization, allowing an attacker to inject arbitrary SQL. This could lead to data exfiltration, authentication bypass, or database manipulation.

### Recommendation
Use parameterized queries (prepared statements) for all database interactions. Never concatenate user input directly into SQL strings.