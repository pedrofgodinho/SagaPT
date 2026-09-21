## Reflected XSS in Request Friend Username Field

- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Endpoint:** `/request_friend` (POST)
- **Vulnerable Parameter:** `username`
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** Submitting the payload via POST to `/request_friend` returned an error message that reflected the unescaped payload: `@<script>alert(1)</script> does not exist`. The script tag appeared raw in the HTML response body.
- **Impact:** An attacker could craft a malicious link to `/request_friend` with the XSS payload in the `username` parameter, causing the script to execute when a victim visits the link.