## XSS Test Results — Settings, Direct Messages, Request Friend, Remove Friend, Remove Request

### 1. POST `/settings` (name, bio, photo_url fields)
- **Payloads:** `<script>alert(1)</script>` in `name`, `bio`, `photo_url`
- **Result:** CANNOT TEST — the form requires `enctype="multipart/form-data"` which is not supported by the scanning tool. POST requests with `application/json` or `application/x-www-form-urlencoded` return HTTP 400 Bad Request.
- **Verdict:** NOT TESTABLE — tool limitation prevents testing this endpoint.

### 2. POST `/direct_messages` (message field)
- **Payload:** `<script>alert(1)</script>` in `message` textarea
- **Result:** Message was stored server-side but HTML-encoded in the response:
  ```html
  <div class="chat-bubble llm-bubble">
      &lt;script&gt;alert(1)&lt;/script&gt;
  </div>
  ```
- **Verdict:** NOT VULNERABLE — proper output encoding applied; stored XSS prevented.

### 3. POST `/request_friend` (username field)
- **Payload:** `<script>alert(1)</script>` in `username` hidden field
- **Result:** XSS payload reflected UNESCAPED in flash error message:
  ```html
  <div class="flash mb-2 error">@<script>alert(1)</script> does not exist</div>
  ```
- **Verdict:** **VULNERABLE** — Confirmed reflected XSS. (See separate finding: `reflected_xss_request_friend_username.md`)

### 4. POST `/remove_friend` (username field)
- **Payload:** `<script>alert(1)</script>` in `username` hidden field
- **Result:** Returned error "Introduce an existing friend." — the payload is NOT reflected anywhere in the response.
- **Verdict:** NOT VULNERABLE — no reflection of user input.

### 5. POST `/remove_request` (username and origin fields)
- **Payloads:** `username=<script>alert(1)</script>`, `origin=<script>alert(2)</script>`
- **Result:** Returned success message "Friendship request was removed" — neither payload is reflected in the response.
- **Verdict:** NOT VULNERABLE — no reflection of user input.

### Summary Table

| Endpoint | Parameter | Reflected? | Encoded? | XSS Vulnerable? |
|----------|-----------|------------|----------|-----------------|
| `/settings` POST | name, bio, photo_url | N/A | N/A | NOT TESTABLE (multipart/form-data required) |
| `/direct_messages` POST | message | Yes | Yes (HTML entities) | No |
| `/request_friend` POST | username | Yes | No | **Yes — Reflected XSS** |
| `/remove_friend` POST | username | No | N/A | No |
| `/remove_request` POST | username, origin | No | N/A | No |

### Conclusion
One confirmed reflected XSS vulnerability was found on the `/request_friend` endpoint (username parameter). The `/settings` endpoint could not be tested due to its requirement for `multipart/form-data` encoding. All other tested endpoints either properly encode output or do not reflect user input.