**Vulnerability Class:** Stored Cross-Site Scripting (XSS)
**Endpoint:** POST `/settings`
**Parameter:** `name`
**Detection Payload:** `<script>alert(1)</script>`
**Evidence:** After submitting the payload via the settings form, the payload is reflected unescaped in multiple pages:
- Profile page (`/profile?username=mr_robot`): `<h4 class="card-title"><script>alert(1)</script></h4>`
- Homepage (`/`): `<script>alert(1)</script> (@mr_robot)` in post card headers
- The settings page itself shows HTML-encoded values (`&lt;script&gt;...`), but the stored data is rendered unescaped when displayed elsewhere.
**Risk:** High — The XSS payload is stored server-side and executed in the browser of any user who views the affected profile or homepage.
**Record:** POST `/settings`, parameter `name`, payload `<script>alert(1)</script>`, unescaped reflection in profile card title and homepage post headers.