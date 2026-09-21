## Stored XSS in POST /edit_post — `content` parameter

**Vulnerability Class:** Stored Cross-Site Scripting (XSS)
**Endpoint:** `POST /edit_post`
**Vulnerable Parameter:** `content` (form field)
**Detection Payload:** `<script>alert(1)</script>`

### Evidence
The payload was submitted via POST to `/edit_post` with `id=19` and `content=<script>alert(1)</script>`. The server stored the updated content and reflected it back unescaped in the homepage response:

```html
<p class="card-text h5"><script>alert(1)</script></p>
```

The `<script>` tag is rendered as raw HTML without any escaping or sanitization, allowing arbitrary JavaScript execution to any user viewing the post.

### Impact
Any user who views the affected post will have the attacker's JavaScript executed in their browser context, potentially leading to session hijacking, credential theft, or actions performed on behalf of the victim.