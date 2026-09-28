## Information Disclosure - API Security Questions Endpoint Exposes All Questions

- **Endpoint:** GET /api/SecurityQuestions
- **Auth Required:** No (publicly accessible)
- **Evidence:** Returns 200 OK with JSON containing all 14 security questions:
  ```json
  [
    {"id":1,"question":"Your eldest siblings middle name?"},
    {"id":2,"question":"Mother's maiden name?"},
    {"id":3,"question":"Mother's birth date? (MM/DD/YY)"},
    {"id":4,"question":"Father's birth date? (MM/DD/YY)"},
    {"id":5,"question":"Maternal grandmother's first name?"},
    {"id":6,"question":"Paternal grandmother's first name?"},
    {"id":7,"question":"Name of your favorite pet?"},
    {"id":8,"question":"Last name of dentist when you were a teenager? (Do not include 'Dr.')"},
    {"id":9,"question":"Your ZIP/postal code when you were a teenager?"},
    {"id":10,"question":"Company you first work for as an adult?"},
    {"id":11,"question":"Your favorite book?"},
    {"id":12,"question":"Your favorite movie?"},
    {"id":13,"question":"Number of one of your customer or ID cards?"},
    {"id":14,"question":"What's your favorite place to go hiking?"}
  ]
  ```

- **Impact:** Attackers can use these questions for social engineering, account takeover via password reset, and OSINT attacks. Combined with the /api/Feedbacks endpoint (which shows partially masked user emails), attackers can correlate security questions with real users.

- **Risk:** High - Enables account takeover via security question abuse