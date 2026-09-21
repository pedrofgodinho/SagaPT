## Stored XSS in Settings Bio Field

- **Vulnerability Class:** Stored Cross-Site Scripting (XSS)
- **Endpoint:** `/settings` (POST)
- **Vulnerable Parameter:** `bio`
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** After submitting the payload via POST to `/settings`, visiting `/profile?username=mr_robot` showed the raw, unescaped `<script>alert(1)</script>` in the profile bio paragraph: `<p class="card-text"><script>alert(1)</script></p>`. The settings page itself HTML-escaped it (`&lt;script&gt;`), but the profile page rendered it as raw HTML.
- **Impact:** Any user viewing mr_robot's profile will execute the injected script in their browser.