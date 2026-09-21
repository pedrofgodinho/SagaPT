**Vulnerability Class:** SQL Injection (Error-based)

**Endpoint:** GET `/direct_messages?username=`

**Vulnerable Parameter:** `username`

**Detection Payload:** `admin' trash` (URL-encoded: `admin%27%20trash`)

**Evidence:** The request returns HTTP 500 Internal Server Error with body:
```
The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.
```
The 500 error triggered by injecting a single quote confirms the parameter is not properly parameterized.

**Impact:** An attacker can inject arbitrary SQL into the direct messages query, potentially reading, modifying, or deleting data from the database.

**Confidence:** Medium-High — 500 error on quote injection confirms SQL error, though the exact error text is not exposed in the response.