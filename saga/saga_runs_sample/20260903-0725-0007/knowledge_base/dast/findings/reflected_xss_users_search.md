## Reflected XSS in GET /users — `search` parameter

**Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
**Endpoint:** `GET /users`
**Vulnerable Parameter:** `search` (query parameter)
**Detection Payload:** `<script>alert(1)</script>`

### Evidence
The payload was submitted via GET to `/users?search=<script>alert(1)</script>`. The server reflected the payload unescaped in the response:

```html
<h6>0 matches for <script>alert(1)</script></h6>
```

The `<script>` tag is rendered as raw HTML without any escaping or sanitization.

### Impact
An attacker could craft a malicious URL to `/users?search=<script>...` and trick a victim into visiting it. The script would execute in the victim's browser context.