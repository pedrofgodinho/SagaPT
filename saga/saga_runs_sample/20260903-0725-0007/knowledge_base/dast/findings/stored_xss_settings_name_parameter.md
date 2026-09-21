## Stored XSS in POST /settings — `name` parameter

**Vulnerability Class:** Stored Cross-Site Scripting (XSS)
**Endpoint:** `POST /settings`
**Vulnerable Parameter:** `name` (form field)
**Detection Payload:** `<script>alert(1)</script>`

### Evidence
The payload was submitted via POST to `/settings` with `name=<script>alert(1)</script>`. The server stored the name and reflected it back unescaped on the profile page at `GET /profile?username=mr_robot`:

```html
<h4 class="card-title"><script>alert(1)</script></h4>
```

The `<script>` tag is rendered as raw HTML without any escaping or sanitization, allowing arbitrary JavaScript execution to any user viewing the profile.

### Impact
Any user who views the affected profile will have the attacker's JavaScript executed in their browser context, potentially leading to session hijacking, credential theft, or actions performed on behalf of the victim.