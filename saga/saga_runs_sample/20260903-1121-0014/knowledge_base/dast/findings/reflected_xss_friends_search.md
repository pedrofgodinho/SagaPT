## Reflected XSS in /friends?username=admin&search

- **Endpoint:** `GET http://www.hackergram.com/friends?username=admin&search=`
- **Vulnerable Parameter:** `search` (the `username` parameter is properly escaped)
- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Detection Payloads:**
  1. `<script>alert(1)</script>`
  2. `"><script>alert(1)</script>`
  3. `<img src=x onerror=alert(1)>`
- **Evidence:** All three payloads are reflected **unescaped** in the HTML response body within the text:
  ```html
  <h6>0 matches for <script>alert(1)</script></h6>
  ```
  and
  ```html
  <h6>0 matches for "><script>alert(1)</script></h6>
  ```
  and
  ```html
  <h6>0 matches for <img src=x onerror=alert(1)></h6>
  ```
- **Impact:** An attacker could craft a malicious URL to deliver arbitrary JavaScript to any user who clicks the link, enabling session hijacking, credential theft, or defacement.
- **Mitigation:** Implement output encoding (HTML entity encoding) for all user-supplied data rendered in the response.