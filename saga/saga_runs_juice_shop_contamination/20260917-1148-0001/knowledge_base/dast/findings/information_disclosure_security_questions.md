## Information Disclosure via Security Questions Endpoint

**Endpoint:** GET /api/SecurityQuestions
**Vulnerability Class:** Information Disclosure

### Detection

The `/api/SecurityQuestions` endpoint returns all 14 security questions in the system without any authentication requirement. This endpoint is publicly accessible.

### Evidence

Request: `GET /api/SecurityQuestions` (unauthenticated)
Response: HTTP 200 with body containing all security questions:
```json
{
  "status": "success",
  "data": [
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
}
```

### Impact

An attacker can:
- Enumerate all security questions used by the application for account recovery
- Use this information to craft targeted social engineering attacks
- Attempt brute-force or dictionary attacks against user security answers
- Correlate security questions with user accounts (if combined with other data)

### Recommendation

Remove or restrict access to the security questions endpoint. Security questions should only be returned in the context of a specific user's account during account recovery, not as a global enumeration endpoint.