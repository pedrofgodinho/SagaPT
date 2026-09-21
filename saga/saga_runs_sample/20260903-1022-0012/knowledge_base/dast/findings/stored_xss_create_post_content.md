## Vulnerability: Stored Cross-Site Scripting (XSS) in `/create_post`

- **Endpoint:** `POST /create_post`
- **Vulnerable Parameter:** `content`
- **Detection Payload:** `"><script>alert(1)</script>`
- **Evidence:** The payload is reflected raw/unescaped in the HTML response body after submission:
  ```html
  <p class="card-text h5">"><script>alert(1)</script></p>
  ```
  The double-quote (`"`), angle brackets (`<`, `>`), and script tags are all reflected without HTML encoding.
- **Vulnerability Class:** Stored XSS (CWE-79)
- **Status:** Confirmed