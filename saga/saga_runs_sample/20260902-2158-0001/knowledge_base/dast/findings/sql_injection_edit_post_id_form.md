**Vulnerability:** SQL Injection in POST `/edit_post` id form field

**Endpoint:** POST /edit_post

**Parameter:** id (form field)

**Detection Payload:** 1' (single quote appended to integer value)

**Evidence:** The response returned HTTP 500 Internal Server Error. A valid baseline request with `id=1` and normal content returned HTTP 200 with normal application logic ("You cannot edit other users' posts"). The single quote payload caused a 500 error, confirming the id parameter is processed by SQL query logic without proper type handling or parameterization.

**Impact:** The parameter is concatenated into a SQL query without parameterization, allowing an attacker to alter query structure.

**Risk:** High — 500 error on single quote confirms injectability.