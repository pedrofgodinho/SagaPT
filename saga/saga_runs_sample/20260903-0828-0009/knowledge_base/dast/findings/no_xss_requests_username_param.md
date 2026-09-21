**Vulnerability Class:** Reflected Cross-Site Scripting (XSS) — NOT PRESENT
**Endpoint:** GET `/requests`
**Parameter:** `username` (query string)
**Detection Payload:** `<script>alert(1)</script>`
**Evidence:** The payload was URL-encoded and sent as `?username=%3Cscript%3Ealert(1)%3C/script%3E`. The response body (200 OK) does NOT contain the XSS payload. The parameter value is not reflected in the HTML output.
**Conclusion:** No reflected XSS vulnerability detected on the `username` parameter.