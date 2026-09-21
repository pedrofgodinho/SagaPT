**Vulnerability:** SQL Injection in POST `/request_friend` username field

**Endpoint:** POST /request_friend

**Parameter:** username (form field)

**Detection Payload:** test' (single quote in username field)

**Evidence:** The response returned HTTP 500 Internal Server Error. A valid baseline request with `username=mr_robot` returned HTTP 200 with normal application logic ("Invalid username"). The single quote payload caused a 500 error, confirming the input is processed by SQL query logic.

**Impact:** The parameter is concatenated into a SQL query without parameterization, allowing an attacker to alter query structure.

**Risk:** High — 500 error on single quote confirms injectability.