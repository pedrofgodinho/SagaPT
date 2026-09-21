## Vulnerability: Reflected Cross-Site Scripting (XSS) in `/request_friend`

- **Endpoint:** `POST /request_friend`
- **Vulnerable Parameter:** `username`
- **Detection Payload:** `"><script>alert(1)</script>`
- **Evidence:** The payload is reflected raw/unescaped in the HTML response body in the error message:
  ```html
  <div class="flash mb-2 error">@"><script>alert(1)</script> does not exist</div>
  ```
  The double-quote (`"`), angle brackets (`<`, `>`), and script tags are all reflected without HTML encoding.
- **Vulnerability Class:** Reflected XSS (CWE-79)
- **Status:** Confirmed