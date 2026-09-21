## Vulnerability: Reflected Cross-Site Scripting (XSS) in `/users?search`

- **Endpoint:** `GET /users?search=`
- **Vulnerable Parameter:** `search`
- **Detection Payload:** `"><script>alert(1)</script>`
- **Evidence:** The payload is reflected raw/unescaped in the HTML response body:
  ```html
  <h6>0 matches for "><script>alert(1)</script></h6>
  ```
  The double-quote (`"`), angle brackets (`<`, `>`), and script tags are all reflected without HTML encoding.
- **Vulnerability Class:** Reflected XSS (CWE-79)
- **Status:** Confirmed

## Non-vulnerable endpoints (for reference)

- `/friends?search=` — Payload not reflected; endpoint requires `username` parameter.
- `/messages?search=` — Payload is HTML-encoded (`"` → `&#34;`, `<` → `&lt;`, `>` → `&gt;`); properly escaped.