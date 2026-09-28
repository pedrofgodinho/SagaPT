## Stored XSS in Feedback Comments

- **Endpoint:** GET http://juiceshop.local:3000/api/Feedbacks
- **Vulnerability Class:** Stored Cross-Site Scripting (XSS)
- **Detection Payload:** N/A - observed in existing data
- **Evidence:** Existing feedback entries in the API response contain raw HTML tags stored in the `comment` field:
  - Feedback id=5: `"...Can't even upload photo of broken purchase!<br /><em>Support Team: Sorry, only order confirmation PDFs can be attached to complaints!</em>..."`
  - Feedback id=6: `"This is <b>the</b> store for awesome stuff of all kinds!..."`
  These HTML tags are stored in the database and returned unescaped in the JSON response. When rendered by a client application, these tags would execute as HTML/JavaScript.
- **Impact:** An attacker who can submit feedback (via the web UI or the `/api/Feedbacks` POST endpoint) can inject arbitrary HTML and JavaScript that will be stored and served to all users who view the feedback list. This enables persistent XSS attacks against any user viewing the feedback data.
- **Priority:** HIGH - stored XSS with persistent impact.