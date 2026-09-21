## No Reflected XSS in /direct_messages POST — message field

- **Endpoint:** `POST /direct_messages`
- **Parameter:** `message` (form field)
- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS) — NOT PRESENT
- **Detection Payload:** `<script>alert(1)</script>`
- **Evidence:** After submitting the payload via POST, the response HTML-escaped the input:
  ```html
  &lt;script&gt;alert(1)&lt;/script&gt;
  ```
- **Conclusion:** The application properly encodes user input in the message field, preventing XSS.