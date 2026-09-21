## SQL Injection in /direct_messages POST

- **Endpoint**: `POST /direct_messages`
- **Parameter**: `username` (form field)
- **Vulnerability Class**: SQL Injection (MySQL)
- **Detection Payload**: `mr_robot'` (single quote appended to benign username)
- **Evidence**: The application returned a 500 Internal Server Error when the single quote was submitted. Both `'` and `' trash` payloads produce the same 500 error response.
- **HTTP Status**: 500 Internal Server Error
- **ZAP Alert**: Application Error Disclosure (pluginId 90022), Information Disclosure - Debug Error Messages (pluginId 10023)
- **Impact**: An attacker can inject arbitrary SQL into the direct message username query, potentially reading, modifying, or deleting database contents.
- **Root Cause**: User input in the `username` form field is concatenated directly into SQL queries without parameterization or escaping.
- **Note**: The `message` form field was also tested with `'` and did NOT trigger SQL errors — it appears to be safe.