## SQL Injection in /request_friend (POST)

- **Endpoint**: `POST /request_friend`
- **Parameter**: `username` (form field)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `'` (single quote in the username form field)
- **Evidence**: The application returned a 500 Internal Server Error when the single quote was submitted. Both `'` and `' trash` payloads produce the same 500 error response.
- **HTTP Status**: 500 Internal Server Error
- **ZAP Alert**: Application Error Disclosure (pluginId 90022), Information Disclosure - Debug Error Messages (pluginId 10023)
- **Impact**: An attacker can inject arbitrary SQL into the friend request query, potentially reading, modifying, or deleting database contents.
- **Root Cause**: User input in the `username` form field is concatenated directly into SQL queries without parameterization or escaping.