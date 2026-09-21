# Stored XSS via Security Question Answer Field

## Vulnerability Class
Stored Cross-Site Scripting (XSS)

## Endpoint
- POST http://juiceshop.local:3000/api/Users (registration)

## Vulnerable Parameter
`securityQuestion.answer`

## Detection Payload
```json
{
  "username": "xss_user3",
  "password": "password123",
  "email": "xss3@test.com",
  "securityQuestion": {"id": 1, "answer": "<script>alert(1)</script>"}
}
```

## Evidence
- Registration returned HTTP 201 with user ID 30
- The `<script>alert(1)</script>` payload was stored in the securityAnswer field without HTML sanitization
- Other fields (username, email) were sanitized to empty strings by the application, but the securityAnswer field accepted raw HTML/JavaScript

## Severity
**MEDIUM** - Stored XSS requires victim to view the user profile or data where the answer is displayed.

## Impact
- Script execution in context of any user viewing the stored answer
- Potential session hijacking, credential theft, or action execution as victim
- The XSS payload persists in the database and will execute for every viewer