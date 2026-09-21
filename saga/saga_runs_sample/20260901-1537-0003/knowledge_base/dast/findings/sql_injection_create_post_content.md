## SQL Injection in /create_post - content field

- **Endpoint:** POST /create_post
- **Parameter:** content
- **Detection payload:** `test post'` (single quote appended to content value)
- **Evidence:** Response returned HTTP 200 with visible MySQL error message: `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''test post'')' at line 1")`
- **ZAP Alert:** Application Error Disclosure (pluginId 90022) with evidence "You have an error in your SQL syntax"
- **Type:** Error-based SQL injection — raw SQL error exposed in response body
- **Priority:** High — visible SQL error message exposes database syntax details

## Additional probes tested
- Payload `' OR '1'='1` in content field: tested separately (see below)