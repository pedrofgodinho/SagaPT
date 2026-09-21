## Vulnerability Class
Reflected Cross-Site Scripting (XSS)

## Endpoint
`POST /create_post`

## Vulnerable Parameter
`content` (form field)

## Detection Payload
`<script>alert(1)</script>`

## Evidence
The payload is reflected **unescaped** in the HTML response body:
```html
<p class="card-text h5"><script>alert(1)</script></p>
```
The `<script>` tags are rendered as literal HTML in the page body inside a `<p>` element. No HTML entity encoding is applied to the user-supplied input.

## Record
- Endpoint: POST /create_post
- Parameter: content
- Payload: &lt;script&gt;alert(1)&lt;/script&gt;
- Evidence: Payload appears unescaped in the homepage response after post creation