## Reflected XSS in POST /request_friend

- **Endpoint:** POST http://www.hackergram.com/request_friend
- **Vulnerable Parameter:** `username` (hidden form field)
- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** The payload was reflected unescaped in the error message in the HTML response body:
  ```html
  <div class="flash mb-2 error">@<script>alert(1)</script> does not exist</div>
  ```
- **Impact:** An attacker could craft a malicious form submission to deliver arbitrary JavaScript to a victim user.
- **Mitigation:** Implement output encoding (HTML entity encoding) for all user-supplied data rendered in HTML responses.