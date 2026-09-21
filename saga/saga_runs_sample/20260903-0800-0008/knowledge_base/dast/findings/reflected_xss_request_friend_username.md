## Reflected XSS in /request_friend username parameter

- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Endpoint:** POST `/request_friend`
- **Vulnerable Parameter:** `username` (hidden form field)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** When submitting a non-existent username, the application reflects the raw payload in the flash error message:
  ```html
  <div class="flash mb-2 error">@<script>alert(1)</script> does not exist</div>
  ```
  The `<script>` tags are NOT HTML-encoded, allowing direct script execution.
- **Context:** Reflected inside a `<div class="flash mb-2 error">` element — a context where browser will execute the script.
- **Impact:** An attacker could craft a malicious request to `/request_friend` with an XSS payload in the `username` field and trick a victim into submitting it (e.g., via CSRF or social engineering), causing arbitrary JavaScript execution in the victim's browser.