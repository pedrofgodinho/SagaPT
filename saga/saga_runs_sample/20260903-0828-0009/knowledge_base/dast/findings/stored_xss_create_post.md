**Vulnerability Class:** Stored Cross-Site Scripting (XSS)
**Endpoint:** POST `/create_post`
**Parameter:** `content` (form field)
**Detection Payload:** `<script>alert(1)</script>`
**Evidence:** The payload is reflected unescaped in the HTML response body as: `<p class="card-text h5"><script>alert(1)</script></p>`. The payload is also stored server-side and persists in the feed on subsequent page loads. No HTML entity encoding or output escaping is applied to user-supplied input.
**Impact:** An attacker can inject malicious JavaScript that executes in the context of any user viewing the post, enabling session hijacking, credential theft, or defacement.