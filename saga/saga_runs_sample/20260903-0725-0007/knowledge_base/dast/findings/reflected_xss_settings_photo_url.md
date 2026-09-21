## Reflected XSS in POST /settings — `photo_url` parameter

**Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
**Endpoint:** `POST /settings`
**Vulnerable Parameter:** `photo_url` (form field)
**Detection Payload:** `<script>alert(1)</script>`

### Evidence
The payload was submitted via POST to `/settings` with `photo_url=<script>alert(1)</script>`. The server attempted to fetch the URL (which failed), and reflected the payload unescaped in the flash error message:

```html
<div class="flash mb-2 error">Failed to download image from URL: unknown url type: 'script>alert(1)</script'</div>
```

The `<script>` tag is rendered as raw HTML without any escaping or sanitization in the flash message.

### Impact
An attacker could craft a malicious POST request to `/settings` with the XSS payload in the `photo_url` parameter. When the victim submits the settings form, the script executes in their browser context via the flash error message.