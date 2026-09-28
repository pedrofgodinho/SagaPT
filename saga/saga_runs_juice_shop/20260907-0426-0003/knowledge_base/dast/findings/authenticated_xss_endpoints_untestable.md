# Authenticated XSS Endpoints - Unable to Test

- **Endpoints**:
  - `POST /api/Complaints` (requires JWT Bearer token)
  - `POST /api/Feedbacks` (requires captchaId)
- **Limitation**: The scanning tools (http_get, http_post) do not support custom Authorization headers with Bearer JWT tokens. All authenticated endpoints returned HTTP 401 with the error: `No Authorization header was found`.
- **Impact**: Cannot confirm or deny XSS in:
  - Complaint `message` field (stored XSS)
  - Feedback `comment` field (stored XSS, blocked by captcha)
- **Recommendation**: These endpoints should be tested with a tool that supports Bearer token authentication.