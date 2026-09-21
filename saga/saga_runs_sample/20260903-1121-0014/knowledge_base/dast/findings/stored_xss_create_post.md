## Stored XSS in POST /create_post

- **Endpoint:** `POST http://www.hackergram.com/create_post`
- **Vulnerable Parameter:** `content` (textarea field)
- **Vulnerability Class:** Stored Cross-Site Scripting (XSS)
- **Detection Payloads:**
  1. `<script>alert(1)</script>`
  2. `"><img src=x onerror=alert(1)>`
- **Evidence:** Both payloads are reflected **unescaped** in the HTML response body within the post card:
  ```html
  <p class="card-text h5"><script>alert(1)</script></p>
  ```
  and
  ```html
  <p class="card-text h5">"><img src=x onerror=alert(1)></p>
  ```
- **Impact:** An attacker can craft a malicious post that will execute arbitrary JavaScript in the browser of any user who views the post (e.g., on the homepage feed or their profile). This enables session hijacking, credential theft, or defacement.
- **Mitigation:** Implement output encoding (HTML entity encoding) for all user-supplied data rendered in HTML responses.