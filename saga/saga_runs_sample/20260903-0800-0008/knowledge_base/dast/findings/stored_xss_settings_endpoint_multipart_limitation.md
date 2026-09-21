## Stored XSS in /settings — Cannot Confirm (Multipart Form Data Limitation)

- **Vulnerability Class:** Potential Stored Cross-Site Scripting (XSS)
- **Endpoint:** POST `/settings`
- **Vulnerable Parameters:** `name`, `bio`, `photo_url`
- **Detection Payloads:** `<script>alert(1)</script>` (name), `<script>alert(2)</script>` (bio), `<script>alert(3)</script>` (photo_url)
- **Evidence:** 
  - The form requires `enctype="multipart/form-data"` which is NOT supported by the scanning tool (`http_post` only supports `application/json` and `application/x-www-form-urlencoded`).
  - Both JSON and form-encoded POSTs to `/settings` return HTTP 400 Bad Request.
  - GET analysis shows values ARE reflected in multiple contexts:
    - `name` → `<input value="...">` on settings page, `<h4>...</h4>` on profile page
    - `bio` → `<textarea>...</textarea>` on settings page, `<p>...</p>` on profile page
  - The application has a confirmed stored XSS vulnerability in `/create_post` content field (same application), indicating inconsistent output encoding.
  - The `/direct_messages` message field IS properly HTML-encoded, showing inconsistent protection.
- **Risk Assessment:** HIGH — Given the confirmed stored XSS in `/create_post` and the reflection of settings fields in executable contexts (h4, p, input value), these parameters are very likely vulnerable to stored XSS if multipart/form-data submission were possible.
- **Impact:** All visitors to the profile page or settings page would have the attacker's script executed if a stored XSS payload were successfully submitted.
- **Tool Limitation:** The scanning tool cannot send `multipart/form-data` requests. This finding represents a high-risk potential vulnerability that could not be confirmed due to tool limitations.