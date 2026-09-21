**Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
**Endpoint:** GET `/users?search=`
**Parameter:** `search`
**Detection Payload:** `<script>alert(1)</script>`
**Evidence:** The payload is reflected unescaped in the HTML response body:
```html
<h6>0 matches for <script>alert(1)</script></h6>
```
The input appears directly inside an `<h6>` element without any HTML entity encoding, making it executable in the victim's browser.
**Risk:** High — An attacker could craft a malicious URL to execute arbitrary JavaScript in a victim's browser.