## No Validation of Security Question Answers on Registration

**Endpoint:** POST /api/Users/
**Vulnerability Class:** Broken Access Control / Missing Validation

### Evidence
Registration accepts arbitrary values for `securityQuestion.answer` without validation:
- Payload: `{"email": "sq_test@test.com", "password": "testpass", "name": "testuser", "securityQuestion": {"id": 1, "answer": "admin"}}`
- Returns 201 with "success" status
- The answer "admin" is stored as-is without any validation or verification

### Impact
An attacker can register accounts with any security question answer, or potentially exploit this to set predictable answers that could be guessed later. Since security questions are publicly accessible (see related finding), an attacker could pre-guess answers for target accounts.