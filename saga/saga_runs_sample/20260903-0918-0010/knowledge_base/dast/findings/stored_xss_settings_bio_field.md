## Stored Cross-Site Scripting in /settings (bio field)

- **Vulnerability Class:** Stored Cross-Site Scripting (XSS)
- **Endpoint:** `POST /settings`
- **Parameter:** `bio` (textarea)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** After submitting the payload via POST `/settings` with the `bio` field, the value is reflected unescaped in the HTML response body on the profile page (`GET /profile?username=mr_robot`):
  ```html
  <p class="card-text"><script>alert(1)</script></p>
  ```
  The script tag is rendered as raw HTML without any escaping, causing it to execute in the browser of any user viewing the profile.
- **Impact:** An attacker can store arbitrary JavaScript in their own bio via the settings page. When any user views the attacker's profile, the script executes in their browser context, potentially stealing session cookies or performing actions as the victim.
- **Remediation:** Apply HTML entity encoding to the `bio` field value before rendering it in HTML on the profile page.