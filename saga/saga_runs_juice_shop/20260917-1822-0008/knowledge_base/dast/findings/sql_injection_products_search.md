## SQL Injection in /api/Products Search Parameter

- **Endpoint:** GET http://juiceshop.local:3000/api/Products?search=
- **Parameter:** search (query string)
- **Vulnerability Class:** SQL Injection
- **Detection Payload:** `' OR '1'='1` in the search parameter
- **Evidence:** Normal search query `?search=test` and SQLi payload `?search=' OR '1'='1` both return HTTP 200 with identical response body (Content-Length: 16011) containing ALL products. The search filter is completely bypassed - no filtering by search term occurs. The recon agent confirmed that `' OR '1'='1` returns all 35+ products regardless of the search term. Additionally, a bare single quote `'` also returns all products without error, suggesting the search uses LIKE which may tolerate the quote, but the `' OR '1'='1` payload structurally bypasses the WHERE clause.
- **Impact:** Search parameter is not properly parameterized. Attacker can bypass search filtering to enumerate all products. Potentially exploitable for UNION-based extraction or data exfiltration.
- **Priority:** HIGH - SQL injection in search parameter allowing data enumeration.