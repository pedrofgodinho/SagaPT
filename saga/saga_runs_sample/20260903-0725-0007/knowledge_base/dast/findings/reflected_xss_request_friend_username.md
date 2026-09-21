## Reflected XSS in POST /request_friend — `username` parameter

**Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
**Endpoint:** `POST /request_friend`
**Vulnerable Parameter:** `username` (form field)
**Detection Payload:** `<script>alert(1)</script>`

### Evidence
The payload was submitted via POST to `/request_friend` with `username=<script>alert(1)</script>`. The server reflected the payload unescaped in the homepage response error message:

```html
<div class="flash mb-2 error">@<script>alert(1)</script> does not exist</div>
```

The `<script>` tag is rendered as raw HTML without any escaping or sanitization.

### Impact
An attacker could craft a malicious link to `/request_friend` with the XSS payload embedded in the `username` parameter. When a victim clicks the link, the script executes in their browser context.