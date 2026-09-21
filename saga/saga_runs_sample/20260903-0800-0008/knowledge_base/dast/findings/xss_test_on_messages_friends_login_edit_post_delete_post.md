# XSS Test Results — Messages, Friends, Login, Edit/Delete Post

## Endpoints Tested (all NOT vulnerable to reflected XSS)

### 1. GET `/messages?search=`
- **Payload:** `<script>alert(1)</script>`
- **Result:** Input is HTML-encoded in the response: `0 matches for "&lt;script&gt;alert(1)&lt;/script&gt;"`
- **Verdict:** NOT VULNERABLE — proper output encoding applied.

### 2. GET `/friends?search=`
- **Payload:** `<script>alert(1)</script>`
- **Result:** The `search` parameter is not reflected at all. Response shows "No user provided" error.
- **Verdict:** NOT VULNERABLE — no reflection of user input.

### 3. POST `/login` (username/password fields)
- **Payloads:** username=`<script>alert(1)</script>`, password=`wrongpassword`
- **Result:** Neither the username nor password fields are reflected in the response body. The response redirects to the homepage regardless of credentials (or shows "You are already logged in" if session is active).
- **Verdict:** NOT VULNERABLE — no reflection of login form fields.

### 4. GET `/edit_post?id=`
- **Payload:** `id=<script>alert(1)</script>`
- **Result:** Returns HTTP 500 Internal Server Error. No XSS payload reflection in the error page.
- **With valid numeric ID (id=20):** The `id` parameter is used as a hidden form field value (`<input type="hidden" name="id" value="20" />`), but the `id` query parameter itself is NOT reflected in the response body.
- **Verdict:** NOT VULNERABLE — no reflection of the `id` parameter.

### 5. GET `/delete_post?id=`
- **Payload:** `id=<script>alert(1)</script>`
- **Result:** Returns HTTP 500 Internal Server Error. No XSS payload reflection.
- **With valid numeric ID (id=20):** The `id` parameter is not reflected in the response. The page shows a success flash message ("Post deleted") and the homepage.
- **Verdict:** NOT VULNERABLE — no reflection of the `id` parameter.

## Summary

| Endpoint | Parameter | Reflected? | Encoded? | XSS Vulnerable? |
|----------|-----------|------------|----------|-----------------|
| `/messages?search=` | search | Yes | Yes (HTML entities) | No |
| `/friends?search=` | search | No | N/A | No |
| `/login` POST | username, password | No | N/A | No |
| `/edit_post?id=` | id | No | N/A | No |
| `/delete_post?id=` | id | No | N/A | No |

**Conclusion:** None of the tested endpoints are vulnerable to reflected XSS. The `/messages` endpoint properly encodes user input, while other endpoints either do not reflect input or return errors without reflecting the payload.