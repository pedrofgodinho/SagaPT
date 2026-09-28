# Stored XSS in Feedback Endpoint - Blocked by Captcha

- **Vulnerability Class**: Stored Cross-Site Scripting (XSS) - BLOCKED
- **Endpoint**: `POST /api/Feedbacks`
- **Vulnerable Parameter**: `comment`
- **Detection Payload**: `<script>alert('stored XSS')</script>`
- **Result**: The feedback POST endpoint requires a `captchaId` parameter. Without it, the request returns HTTP 500 with a SQL error: `WHERE parameter "captchaId" has invalid "undefined" value`. This prevents storing arbitrary comment content.
- **Note**: The `/api/Feedbacks` GET endpoint returns JSON containing HTML entities (`<br />`, `<em>`, `<b>`) in existing comments, suggesting the application does render HTML in stored content. However, the captcha requirement blocks direct XSS payload submission.
- **Limitation**: Cannot fully test this vector without a valid captchaId.