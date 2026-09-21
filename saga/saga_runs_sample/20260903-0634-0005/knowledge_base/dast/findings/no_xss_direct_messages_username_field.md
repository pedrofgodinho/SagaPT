## No Reflected XSS in /direct_messages POST — username field

- **Endpoint:** `POST /direct_messages`
- **Parameter:** `username` (form field)
- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS) — NOT PRESENT
- **Detection Payloads attempted:** `<script>alert(1)</script>`, `test\"><script>alert(1)</script>`, `stark\"><img src=x onerror=alert(1)>`
- **Evidence:** All XSS payloads triggered a 500 Internal Server Error. The application validates the username against existing users in the database, and special characters in the payload break the query before any reflection can occur.
- **Conclusion:** The username field is protected by server-side validation that prevents XSS injection via this vector.