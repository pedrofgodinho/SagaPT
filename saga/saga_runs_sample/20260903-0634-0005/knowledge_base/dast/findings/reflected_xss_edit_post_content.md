## Reflected XSS in /edit_post POST — content field

- **Endpoint:** `POST /edit_post`
- **Parameter:** `content` (form field)
- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** After submitting the payload via POST to edit post ID 19, the homepage reflects the payload unescaped in the post card:
  ```html
  <p class="card-text h5"><script>alert(1)</script></p>
  ```
- **Impact:** An attacker who can edit a post can inject malicious JavaScript that executes when any user views that post.