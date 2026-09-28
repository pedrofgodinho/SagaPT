## Information Disclosure - Security Questions API Publicly Accessible

**Vulnerability Class:** Information Disclosure
**Endpoint:** GET /api/SecurityQuestions
**Evidence:**
- Request: GET http://juiceshop.local:3000/api/SecurityQuestions (no authentication)
- Response: HTTP 200 with all 14 security questions returned in plain text
- Questions include: "Your eldest siblings middle name?", "Mother's maiden name?", "Mother's birth date?", "Father's birth date?", "Maternal grandmother's first name?", "Paternal grandmother's first name?", "Name of your favorite pet?", "Last name of dentist when you were a teenager?", "Your ZIP/postal code when you were a teenager?", "Company you first work for as an adult?", "Your favorite book?", "Your favorite movie?", "Number of one of your customer or ID cards?", "What's your favorite place to go hiking?"
- Each question includes its ID (1-14), question text, and timestamps

**Impact:** All security questions needed for account takeover via password reset are publicly available without authentication. An attacker can use these questions to craft targeted phishing or social engineering attacks against users.

**Detection Payload:** GET /api/SecurityQuestions (unauthenticated)