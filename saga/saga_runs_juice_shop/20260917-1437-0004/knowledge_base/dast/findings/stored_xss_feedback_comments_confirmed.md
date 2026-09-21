# Stored XSS in Feedback Comments (DAST Confirmed)

**Endpoint:** POST /api/Feedbacks (submission) / GET /api/Feedbacks (display)
**Vulnerable Parameter:** comment field
**Vulnerability Class:** Stored Cross-Site Scripting (XSS)

## Evidence
The `/api/Feedbacks` endpoint stores and reflects user-supplied content without sanitization or escaping. Existing feedback comments contain unescaped HTML tags:

- Feedback ID 5 contains: `<br /><em>Support Team: Sorry, only order confirmation PDFs can be attached to complaints!</em>`
- Feedback ID 6 contains: `<b>the</b>`

These HTML tags are stored in the database and reflected back in the JSON response without sanitization.

## Detection Payload
Existing feedback data confirms HTML tags are stored and reflected:
- `<br />`, `<em>`, `<b>` tags in feedback comments
- Pre-existing stored XSS confirmed in application data

## Impact
- Any client rendering these JSON responses as HTML would execute embedded HTML/JavaScript
- Potential for session hijacking, credential theft, or other XSS-based attacks
- The feedback list is publicly accessible, making this exploitable by any visitor

## Notes
- This finding was also identified by the recon agent (pre-existing finding)
- The DAST agent confirmed the same vulnerability through direct observation of stored data
- Feedback submission requires a captchaId, limiting direct exploitation but does not mitigate the stored XSS risk