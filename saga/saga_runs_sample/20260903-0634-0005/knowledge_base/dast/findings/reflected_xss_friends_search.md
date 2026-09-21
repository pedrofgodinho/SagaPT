## Reflected XSS in /friends?search=

- **Endpoint:** `GET /friends?search=` (requires `username` parameter)
- **Parameter:** `search`
- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** The payload is reflected unescaped in the HTML response body:
  ```
  <h6>0 matches for <script>alert(1)</script></h6>
  ```
- **Impact:** An attacker could craft a malicious URL to execute arbitrary JavaScript in a victim's browser when they click a link to `/friends?username=...&search=<malicious_payload>`.