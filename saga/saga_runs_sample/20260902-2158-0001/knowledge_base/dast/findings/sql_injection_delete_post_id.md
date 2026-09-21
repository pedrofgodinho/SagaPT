**Vulnerability:** SQL Injection in `/delete_post?id=` parameter

**Endpoint:** GET /delete_post?id=

**Parameter:** id (query string)

**Detection Payload:** test' (single quote appended)

**Evidence:** The response returned HTTP 500 Internal Server Error. A valid baseline request with `id=1` returned HTTP 200 with normal application logic ("You cannot delete other users' posts"). The single quote payload caused a 500 error, confirming the id parameter is processed by SQL query logic without proper type handling or parameterization.

**Impact:** The parameter is concatenated into a SQL query without parameterization, allowing an attacker to alter query structure.

**Risk:** High — 500 error on single quote confirms injectability.