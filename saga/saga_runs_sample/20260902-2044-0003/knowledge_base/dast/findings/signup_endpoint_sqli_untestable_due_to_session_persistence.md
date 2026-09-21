## SQL Injection Testing on /signup — Could Not Confirm

**Endpoint:** POST http://www.hackergram.com/signup
**Parameters tested:** `username`, `name`, `password`
**Payloads attempted:**
- `username`: `'`, `' OR 1=1 --`
- `name`: `'`
- `password`: `' OR 1=1 --`

**Result:** All 9 POST requests returned byte-for-byte identical responses (HTTP 200, 18477 bytes, same HTML body with flash message "You are already logged in"). No SQL error messages, no structural differences, no ZAP alerts.

**Root cause:** The application persists the `mr_robot` session across all requests despite multiple `logout()` calls. The signup form is never processed for logged-in users — the application immediately returns the authenticated homepage. This prevents any injection payloads from reaching the database layer.

**Conclusion:** SQL injection on the signup endpoint **could not be confirmed or ruled out**. The testing was blocked by session management issues. If an unauthenticated user could POST to /signup, the payloads may or may not be vulnerable — further testing with proper unauthenticated access is required.

**Note:** This is a negative finding — the absence of evidence is not evidence of absence. The application may still be vulnerable, but it was not possible to verify due to the session persistence issue.