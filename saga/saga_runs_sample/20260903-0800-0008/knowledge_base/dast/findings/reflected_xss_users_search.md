## Reflected XSS in /users?search=X

- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Endpoint:** GET `/users?search=X`
- **Vulnerable Parameter:** `search` (query string)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** The payload appears unescaped in the HTML response body:
  ```html
  <h6>0 matches for <script>alert(1)</script></h6>
  ```
- **Context:** Reflected inside an `<h6>` element text content, directly executable by any browser.
- **Impact:** An attacker could craft a malicious URL like `/users?search=<script>...</script>` and trick a victim into visiting it, causing arbitrary JavaScript execution in the victim's browser.