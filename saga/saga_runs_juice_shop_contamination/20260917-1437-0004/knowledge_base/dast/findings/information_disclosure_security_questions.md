# Security Questions Information Disclosure

**Endpoint:** `GET /api/SecurityQuestions` (publicly accessible, no auth required)
**Vulnerability Class:** Sensitive Information Disclosure

## Evidence
The endpoint returns all 14 security questions with their IDs:
1. Your eldest siblings middle name?
2. Mother's maiden name?
3. Mother's birth date? (MM/DD/YY)
4. Father's birth date? (MM/DD/YY)
5. Maternal grandmother's first name?
6. Paternal grandmother's first name?
7. Name of your favorite pet?
8. Last name of dentist when you were a teenager? (Do not include 'Dr.')
9. Your ZIP/postal code when you were a teenager?
10. Company you first work for as an adult?
11. Your favorite book?
12. Your favorite movie?
13. Number of one of your customer or ID cards?
14. What's your favorite place to go hiking?

## Detection
```
GET /api/SecurityQuestions
Response: 200 OK
Body: {"status":"success","data":[{"id":1,"question":"Your eldest siblings middle name?",...},...]}
```

## Impact
All security questions used for password reset/account recovery are publicly disclosed. An attacker can use this information to:
- Attempt credential stuffing or password guessing with knowledge of the question types
- Social engineer users by knowing which questions they might use
- Potentially bypass account recovery mechanisms if combined with other information

## Notes
This endpoint requires no authentication and returns all questions without filtering.