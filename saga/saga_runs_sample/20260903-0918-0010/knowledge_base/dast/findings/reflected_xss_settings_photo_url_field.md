## Reflected Cross-Site Scripting in /settings (photo_url field)

- **Vulnerability Class:** Reflected Cross-Site Scripting (XSS)
- **Endpoint:** `POST /settings`
- **Parameter:** `photo_url` (text field)
- **Detection Payload:** `"><script>alert(1)</script>`
- **Evidence:** After submitting the payload via POST `/settings` with the `photo_url` field, the application attempts to download the image and fails, returning an error message that reflects the raw, unescaped payload:
  ```
  Failed to download image from URL: unknown url type: '><script>alert(1)</script>'
  ```
  The `<script>` tag and surrounding characters appear unescaped in the flash error message within the HTML response body.
- **Impact:** An attacker can craft a request to `/settings` with a malicious `photo_url` value. When the settings page is reloaded (or the attacker can force a victim to submit a crafted form), the reflected script executes in the victim's browser.
- **Remediation:** Apply HTML entity encoding to the `photo_url` field value before reflecting it in any error messages or HTML output.