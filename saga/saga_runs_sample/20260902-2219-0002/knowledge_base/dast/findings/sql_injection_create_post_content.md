## SQL Injection in /create_post (POST)

- **Endpoint**: `POST /create_post`
- **Parameter**: `content` (form field)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `'` (single quote in the content form field)
- **Evidence**: The application returned a visible MySQL error in the response body:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''') at line 1")
  ```
- **HTTP Status**: 200 (error message rendered in a red `<h4>` element)
- **ZAP Alert**: Application Error Disclosure (pluginId 90022)
- **Impact**: An attacker can inject arbitrary SQL into the post creation query, potentially reading, modifying, or deleting database contents.
- **Root Cause**: User input is concatenated directly into SQL queries without parameterization or escaping.
- **Note**: The GET `/create_post?content=` query parameter was tested and did NOT trigger SQL errors — it only pre-populates the form client-side. The vulnerability is in the POST `content` form field.