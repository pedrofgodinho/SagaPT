## SQL Injection in /delete_post?id=

- **Vulnerability Class:** SQL Injection (Error-based)
- **Endpoint:** GET `/delete_post`
- **Vulnerable Parameter:** `id` (query string)
- **Detection Payload:** `id='` (bare single quote)
- **Evidence:** The request returns HTTP 500 Internal Server Error. A valid integer ID (`id=1`) returns HTTP 200 with normal page content. The 500 error is triggered specifically by the unescaped single quote, indicating the `id` parameter is concatenated into a SQL query without proper parameterization.
- **Impact:** Confirmed injectable — an attacker could extract data, modify records, or potentially achieve remote code execution depending on the database configuration.