# Stored XSS in Feedback Comments

**Endpoint:** `GET /api/Feedbacks` (publicly accessible)
**Vulnerable Parameter:** `comment` field in feedback submissions
**Vulnerability Class:** Stored Cross-Site Scripting (XSS)

## Evidence
The `/api/Feedbacks` endpoint returns feedback data that contains unescaped HTML tags in the `comment` field. Specifically:
- Feedback ID 5 contains: `<br /><em>Support Team: Sorry, only order confirmation PDFs can be attached to complaints!</em>`
- Feedback ID 6 contains: `<b>the</b>`

These HTML tags are stored in the database and reflected back in the JSON response without sanitization or escaping.

## Detection Payload
Existing feedback comments (pre-existing in the application) contain HTML tags:
- `<br />` tag in feedback ID 5
- `<em>` tags in feedback ID 5
- `<b>` tag in feedback ID 6

## Impact
Any client rendering these JSON responses as HTML (e.g., Angular templates, browser-based viewers) would execute the embedded HTML/JavaScript, potentially leading to session hijacking, credential theft, or other XSS-based attacks.

## Notes
The application appears to store user-provided content without sanitization. The feedback list is publicly accessible, making this exploitable by any visitor.