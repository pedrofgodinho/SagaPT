## Vulnerability: Unauthenticated API Data Exposure

**Endpoint:** `/api/Challenges`, `/api/SecurityQuestions`
**Parameter:** N/A (path-based endpoint)
**Vulnerability Class:** Sensitive Data Exposure / Insecure Direct Object Reference

### Description
The Juice Shop API exposes sensitive data without authentication requirements:
- `/api/Challenges` returns the full list of all challenges (67KB JSON response) including challenge names, descriptions, categories, difficulty levels, and exploit instructions
- `/api/SecurityQuestions` returns all 14 security questions used by the application for password reset

### Evidence
- `GET /api/Challenges` → HTTP 200, Content-Type: application/json, body contains all challenge data
- `GET /api/SecurityQuestions` → HTTP 200, Content-Type: application/json, body contains all 14 security questions with IDs

### Impact
Attackers can enumerate all challenges to understand attack vectors, and retrieve security questions which can be used for account takeover via password reset enumeration.

### Detection Payload
```
GET /api/Challenges HTTP/1.1
Host: juiceshop.local:3000

GET /api/SecurityQuestions HTTP/1.1
Host: juiceshop.local:3000
```

### Risk
Medium - Information disclosure that aids further attacks.