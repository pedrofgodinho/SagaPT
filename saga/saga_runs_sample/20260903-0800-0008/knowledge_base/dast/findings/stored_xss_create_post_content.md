## Stored XSS in /create_post content field

- **Vulnerability Class:** Stored Cross-Site Scripting (XSS)
- **Endpoint:** POST `/create_post`
- **Vulnerable Parameter:** `content` (form field, textarea)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** After submitting the payload via POST, the homepage reflected it unescaped:
  ```html
  <p class="card-text h5"><script>alert(1)</script></p>
  ```
- **Context:** Reflected inside a `<p>` element text content, directly executable.
- **Impact:** Any user visiting the homepage or a profile page will have the attacker's script executed. This is more severe than reflected XSS as no social engineering is needed — the payload persists server-side and affects all visitors.