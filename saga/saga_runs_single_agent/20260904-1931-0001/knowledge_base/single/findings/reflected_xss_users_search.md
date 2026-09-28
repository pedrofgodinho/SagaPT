# Reflected XSS in /users?search

**Endpoint:** `GET /users?search`
**Parameter:** `search`
**Type:** Reflected Cross-Site Scripting
**Risk:** High

## Detection
Sending `<script>alert(1)</script>` to the `search` parameter results in the payload being reflected unescaped in the response body:
```html
<h6>0 matches for <script>alert(1)</script></h6>
```

The script tag is NOT HTML-escaped in the response, allowing arbitrary JavaScript execution.

## Evidence
- URL: `http://www.hackergram.com/users?search=<script>alert(1)</script>`
- Response body contains: `<script>alert(1)</script>` reflected in the search results heading
- No Content Security Policy header to block inline scripts

## Impact
An attacker can craft a malicious URL and trick a user into clicking it, executing arbitrary JavaScript in the victim's browser. This can lead to:
- Session hijacking (stealing cookies)
- Credential phishing
- Defacement
- Keylogging

## PoC
```
http://www.hackergram.com/users?search=<script>alert(document.cookie)</script>
```