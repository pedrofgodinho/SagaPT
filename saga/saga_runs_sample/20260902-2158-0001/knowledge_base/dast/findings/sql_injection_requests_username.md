**Vulnerability:** SQL Injection in `/requests?username=` parameter

**Endpoint:** GET /requests?username=

**Parameter:** username (query string)

**Detection Payload:** test' (single quote appended)

**Evidence:** The response returned HTTP 500 Internal Server Error. A valid baseline request with `username=mr_robot` returned HTTP 200 with normal application logic ("Invalid friendship request"). The single quote payload caused a 500 error while the tautology payload `test' OR '1'='1` returned 200, confirming the single quote is being processed by SQL query logic.

**Impact:** The parameter is concatenated into a SQL query without parameterization, allowing an attacker to alter query structure.

**Risk:** High — 500 error on single quote, normal response on tautology confirms injectability.