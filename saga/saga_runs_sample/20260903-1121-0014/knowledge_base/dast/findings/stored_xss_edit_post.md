## Stored XSS in POST /edit_post

- **Endpoint:** POST http://www.hackergram.com/edit_post
- **Vulnerable Parameter:** `content` (textarea field)
- **Vulnerability Class:** Stored Cross-Site Scripting (XSS)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** After editing post ID 21 (owned by mr_robot), the payload was reflected unescaped in the HTML response body:
  ```html
  <p class="card-text h5"><script>alert(1)</script></p>
  ```
- **Impact:** An attacker who can edit posts can inject arbitrary JavaScript that executes when any user views the post.
- **Mitigation:** Implement output encoding (HTML entity encoding) for all user-supplied data rendered in HTML responses.