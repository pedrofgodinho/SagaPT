## Vulnerability Class
Reflected Cross-Site Scripting (XSS)

## Endpoint
`GET /users?search=<script>alert(1)</script>`

## Vulnerable Parameter
`search` (query parameter)

## Detection Payload
`<script>alert(1)</script>`

## Evidence
The payload is reflected **unescaped** in the HTML response body:
```html
<h6>0 matches for <script>alert(1)</script></h6>
```

The `<script>` tags are rendered as literal HTML in the page body (inside an `<h6>` tag), meaning any JavaScript in the payload would execute when a victim visits this URL.

## Context
The reflection occurs inside the HTML body, directly as text content of an `<h6>` element. No HTML entity encoding is applied to the user-supplied input.

## Other Endpoints Tested (Not Vulnerable)
- `/profile?username=` — No reflection; returns "User does not exist"
- `/friends?username=` — Reflected but HTML-escaped (`&lt;script&gt;...`)
- `/create_post?content=` — Reflected via JavaScript DOM (`urlParams.get('content')` used to set textarea value); not directly in HTML body
- `/messages?search=` — HTML-escaped (`&lt;script&gt;...`)
- `/friends?search=` — No reflection; returns "No user provided"
- `/edit_post?id=` — Returns 500 Internal Server Error; no reflection