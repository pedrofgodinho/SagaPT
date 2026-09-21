# Security Questions Publicly Accessible

**Endpoint:** `GET /api/SecurityQuestions`
**Vulnerability Class:** Sensitive Information Disclosure

## Evidence
The endpoint returns all 14 security questions with their IDs without requiring authentication:
```
GET /api/SecurityQuestions
Response: 200 OK
Body: {"status":"success","data":[{"id":1,"question":"Your eldest siblings middle name?"},...]}
```

All 14 questions returned:
1. Your eldest siblings middle name?
2. Mother's maiden name?
3. Mother's birth date? (MM/DD/YY)
4. Father's birth date? (MM/DD/YY)
5. Maternal grandmother's first name?
6. Paternal grandmother's first name?
7. Name of your favorite pet?
8. Last name of dentist when you were a teenager?
9. Your ZIP/postal code when you were a teenager?
10. Company you first work for as an adult?
11. Your favorite book?
12. Your favorite movie?
13. Number of one of your customer or ID cards?
14. What's your favorite place to go hiking?

## Detection
```
GET /api/SecurityQuestions
Response: 200 OK with full list of all security questions
```

## Impact
- Attackers can enumerate all security questions used for account recovery
- Enables targeted social engineering attacks against users
- Combined with other information disclosure, could facilitate account takeover via password reset

## Notes
This finding was previously recorded by the recon agent in `dast/findings/information_disclosure_security_questions.md`.