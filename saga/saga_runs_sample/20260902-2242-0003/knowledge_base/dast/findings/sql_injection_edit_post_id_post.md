## SQL Injection in /edit_post — POST `id` parameter

- **Vulnerability Class:** SQL Injection (Error-based)
- **Endpoint:** POST `/edit_post`
- **Vulnerable Parameter:** `id` (form field)
- **Detection Payload:** `id=1' trash`
- **Evidence:** The request returns HTTP 500 Internal Server Error with generic error message: "The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application." A valid integer ID (`id=1`) returns HTTP 200 with normal page content. The 500 error is triggered specifically by the unescaped single quote, indicating the `id` parameter is concatenated into a SQL query without proper parameterization.
- **Impact:** An attacker can inject arbitrary SQL into the edit_post query, potentially reading, modifying, or deleting data from the database.
- **Confidence:** Medium — 500 error on quote injection confirms SQL error, though the exact error text is not exposed in the response (unlike the GET `/edit_post` which was already confirmed in prior DAST findings).