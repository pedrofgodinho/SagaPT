**Vulnerability Class:** Stored Cross-Site Scripting (XSS)
**Endpoint:** POST `/settings`
**Parameter:** `bio`
**Detection Payload:** `<script>alert(1)</script>`
**Evidence:** After submitting the payload via the settings form, the payload is reflected unescaped in the profile page:
- Profile page (`/profile?username=mr_robot`): `<p class="card-text"><script>alert(1)</script></p>`
- The bio field renders the raw HTML in the card body on the profile page.
**Risk:** High — The XSS payload is stored server-side and executed in the browser of any user who views the affected profile.
**Record:** POST `/settings`, parameter `bio`, payload `<script>alert(1)</script>`, unescaped reflection in profile card text paragraph.