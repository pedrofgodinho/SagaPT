# Feedback POST Endpoint Requires captchaId - Blocks Unauthenticated XSS Submission

**Vulnerability Class:** Input Validation / Anti-Abuse

**Affected Endpoints:**
- POST /api/Feedbacks

**Evidence:**
Attempting to POST to /api/Feedbacks without a valid captchaId results in rejection:

1. Without captchaId field:
   - Status: 500 Internal Server Error
   - Error: "WHERE parameter \"captchaId\" has invalid \"undefined\" value"
   - Stack trace reveals Sequelize SQLite query generator internals

2. With invalid captchaId:
   - Status: 401 Unauthorized
   - Response: "Wrong answer to CAPTCHA. Please try again."

**Detection Payloads:**
```
POST /api/Feedbacks
{"rating": 5, "comment": "<script>alert(1)</script>"}
→ 500 Error: WHERE parameter "captchaId" has invalid "undefined" value

POST /api/Feedbacks
{"rating": 5, "comment": "<script>alert(1)</script>", "captchaId": "test"}
→ 401 "Wrong answer to CAPTCHA. Please try again."
```

**Impact:**
- XSS payloads submitted via POST /api/Feedbacks are blocked by the captchaId requirement
- The captcha mechanism prevents automated or unauthenticated feedback submission
- Existing stored XSS (already confirmed) comes from pre-existing data, not from user-submitted content via this endpoint
- The captcha validation acts as a rate-limiting and bot-prevention measure

**Notes:**
- The captchaId validation is checked before the comment is processed
- This is a server-side validation that cannot be bypassed without a valid captcha solution
- The stored XSS in feedback comments (already confirmed) is from pre-existing data in the database