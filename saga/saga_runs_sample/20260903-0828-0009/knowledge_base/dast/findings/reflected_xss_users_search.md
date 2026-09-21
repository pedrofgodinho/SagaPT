**Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
**Endpoint:** GET `/users?search=`
**Parameter:** `search` (query string)
**Detection Payload:** `<script>alert(1)</script>`
**Evidence:** The payload is reflected unescaped in the HTML response body as: `<h6>0 matches for <script>alert(1)</script></h6>`. No HTML entity encoding or output escaping is applied to user-supplied input.
**Impact:** An attacker could craft a malicious URL to execute arbitrary JavaScript in a victim's browser when the victim clicks the link or visits the crafted URL.