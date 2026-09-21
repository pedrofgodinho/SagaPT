## Reflected XSS in /create_post POST — content field

- **Endpoint:** `POST /create_post`
- **Parameter:** `content` (form field)
- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** After submitting the payload via POST, the homepage reflects the payload unescaped in the post card:
  ```html
  <p class="card-text h5"><script>alert(1)</script></p>
  ```
- **Impact:** An attacker could craft a malicious post that, when viewed by other users, executes arbitrary JavaScript in their browser.