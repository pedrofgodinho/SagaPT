## Security Questions Publicly Accessible

**Endpoint:** GET /api/SecurityQuestions
**Vulnerability Class:** Information Disclosure

### Evidence
All 14 security questions are retrievable without authentication:
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

### Impact
Attackers can enumerate all security questions to prepare for account takeover via security question answers. When combined with the registration endpoint accepting arbitrary security question answers (no validation), this enables pre-computed brute force attacks against user accounts.