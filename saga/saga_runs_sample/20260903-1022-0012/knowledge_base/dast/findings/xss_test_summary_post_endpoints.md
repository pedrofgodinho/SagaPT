## XSS Testing Summary — POST Endpoints

**Date:** 2026-09-03
**Payload Used:** `"><script>alert(1)</script>`

### Vulnerable Endpoints

| # | Endpoint | Method | Parameter | Result |
|---|----------|--------|-----------|--------|
| 1 | `/create_post` | POST | `content` | **VULNERABLE** — Stored XSS confirmed |
| 2 | `/edit_post` | POST | `content` | **VULNERABLE** — Stored XSS confirmed |
| 4 | `/request_friend` | POST | `username` | **VULNERABLE** — Reflected XSS confirmed |

### Non-Vulnerable Endpoints

| # | Endpoint | Method | Parameter | Result |
|---|----------|--------|-----------|--------|
| 3 | `/direct_messages` | POST | `message` | **NOT VULNERABLE** — Payload HTML-encoded (`&#34;&gt;&lt;script&gt;...`) |
| 5 | `/remove_request` | POST | `username`, `origin` | **NOT VULNERABLE** — Payload not reflected in response |

### Evidence

**`/create_post` (POST `content`):**
- Payload stored and reflected raw in the homepage post list:
  ```html
  <p class="card-text h5">"><script>alert(1)</script></p>
  ```

**`/edit_post` (POST `content`):**
- Payload stored and reflected raw in the homepage post list after edit:
  ```html
  <p class="card-text h5">"><script>alert(1)</script></p>
  ```

**`/request_friend` (POST `username`):**
- Payload reflected raw in the error message:
  ```html
  <div class="flash mb-2 error">@"><script>alert(1)</script> does not exist</div>
  ```

**`/direct_messages` (POST `message`):**
- Payload properly HTML-encoded in chat bubbles:
  ```html
  <div class="chat-bubble llm-bubble">&#34;&gt;&lt;script&gt;alert(1)&lt;/script&gt;</div>
  ```

**`/remove_request` (POST `username`, `origin`):**
- No reflection of the payload in the response; returned success message without echoing input.

### Notes
- No ZAP XSS alerts were triggered for any of these requests.
- All POST form submissions were sent with `content_type="form"` (application/x-www-form-urlencoded).