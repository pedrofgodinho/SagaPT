## XSS - Sort Parameter JSON Reflection

**Vulnerability Class:** Reflected XSS (JSON context only, not HTML)
**Endpoint:** GET /api/Products
**Vulnerable Parameter:** sort
**Detection Payload:** sort=<script>alert(1)</script>
**Evidence:**
- Request: GET http://juiceshop.local:3000/api/Products?sort=<script>alert(1)</script>
- Response: HTTP 400 with body: {"message":"Sorting not allowed on given attributes","errors":["<script>alert(1)</script>"]}
- The payload is reflected in the JSON error array, NOT in HTML context
- This is NOT exploitable as reflected XSS since the response is application/json, not text/html
- No HTML-context reflection found on any tested endpoint

**Tested Payloads (all returned JSON, no HTML reflection):**
- `<script>alert(1)</script>` → JSON reflection in errors array
- `<img src=x onerror=alert(1)>` → JSON reflection in errors array
- `<svg onload=alert(1)>` → JSON reflection in errors array
- `javascript:alert(1)` → No reflection

**Tested Endpoints (no HTML reflection found):**
- /api/Products?sort= (JSON reflection only)
- /api/Products?q= (no reflection)
- /api/Products?search= (no reflection)
- /api/Products?filter= (no reflection)
- /rest/user/login (generic "Invalid email or password." - no reflection)
- / (SPA - no query parameter reflection)
- /api/SecurityQuestions?q= (no reflection)
- /api/Contact (endpoint doesn't exist - 500 "Unexpected path")
- /api/Feedback (endpoint doesn't exist - 500 "Unexpected path")

**Conclusion:** No confirmed HTML-context reflected XSS vulnerability found.