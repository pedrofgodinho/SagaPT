## Reflected XSS in /users?search

- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Endpoint:** `GET /users?search=XXX`
- **Parameter:** `search` (query string)
- **Detection Payloads:**
  1. `"><script>alert(1)</script>`
  2. `"><img src=x onerror=alert(1)>`
  3. `<svg/onload=alert(1)>`
- **Evidence:** All three payloads are reflected unescaped in the HTML response body within the search results `<h6>` element. For example, the script tag payload produces:
  ```html
  <h6>0 matches for "><script>alert(1)</script></h6>
  ```
  The `<img>` and `<svg>` payloads are similarly reflected as raw HTML without any HTML entity encoding.
- **Impact:** An attacker could craft a malicious URL to `/users?search=` containing arbitrary JavaScript that executes in a victim's browser, potentially stealing session cookies or performing actions on behalf of the user.
- **Remediation:** Apply output encoding (HTML entity encoding) to the `search` parameter value before reflecting it in the HTML response. Consider also implementing a Content-Security-Policy header.

**Note:** The `/messages?search=` endpoint was also tested with the same payloads but properly HTML-encodes all user input (e.g., `&lt;script&gt;`), so it is not vulnerable.