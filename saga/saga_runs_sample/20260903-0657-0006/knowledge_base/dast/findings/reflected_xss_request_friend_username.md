## Vulnerability Class
Reflected Cross-Site Scripting (XSS)

## Endpoint
`POST /request_friend`

## Vulnerable Parameter
`username` (hidden form field)

## Detection Payload
`<script>alert(1)</script>`

## Evidence
The payload is reflected **unescaped** in the HTML response body within the flash error message:
```html
<div class="flash mb-2 error">@<script>alert(1)</script> does not exist</div>
```
The `<script>` tags are rendered as literal HTML in the page body. No HTML entity encoding is applied to the user-supplied input.

## Record
- Endpoint: POST /request_friend
- Parameter: username
- Payload: &lt;script&gt;alert(1)&lt;/script&gt;
- Evidence: Payload appears unescaped in the flash error message on the homepage response when the username does not exist