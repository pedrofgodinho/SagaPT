## Stored Cross-Site Scripting in /create_post (POST content field)

- **Vulnerability Class:** Stored Cross-Site Scripting (XSS)
- **Endpoint:** `POST /create_post`
- **Parameter:** `content` (form field / textarea)
- **Detection Payloads:**
  1. `<script>alert(1)</script>`
  2. `<img src=x onerror=alert(1)>`
  3. `<svg/onload=alert(1)>`
- **Evidence:** All three payloads are stored in the database and reflected unescaped in the HTML response body. On the homepage/profile, the payloads appear as raw HTML inside `<p class="card-text h5">` elements:
  ```html
  <p class="card-text h5"><script>alert(1)</script></p>
  <p class="card-text h5"><img src=x onerror=alert(1)></p>
  <p class="card-text h5"><svg/onload=alert(1)></p>
  ```
  Posts were created with IDs 20, 21, and 22 and confirmed visible on `GET /profile?username=mr_robot`.
- **GET Parameter Note:** The GET parameter `?content=XXX` on `/create_post` is NOT vulnerable — it uses `document.getElementById('content').value = content` which safely sets the textarea text value without HTML injection.
- **Impact:** An attacker can submit malicious JavaScript via the post content field. When any user views the affected post (on the homepage, profile, or elsewhere), the script executes in their browser context, potentially stealing session cookies, performing actions as the victim, or defacing the page.
- **Remediation:** Apply HTML entity encoding (e.g., `&lt;script&gt;`) to the `content` field value before rendering it in HTML. Alternatively, use a template engine that auto-escapes output.
