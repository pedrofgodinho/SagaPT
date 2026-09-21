# Challenges Endpoint Public Exposure

## Vulnerability Class
Information Disclosure / Sensitive Data Exposure

## Endpoint
`GET /api/Challenges/`

## Evidence
- Request: `GET http://juiceshop.local:3000/api/Challenges/`
- Response: 200 OK, returns full JSON array of all application challenges
- Contains: challenge keys, names, categories, descriptions, difficulty ratings, MITRE links, tutorial order, and challenge dependencies
- All 17+ challenges exposed including:
  - `passwordHashLeakChallenge` - "Obtain the password (hash) of the currently logged-in user directly from a REST API endpoint."
  - `restfulXssChallenge` - "Perform a persisted XSS attack with <code>&lt;iframe src=javascript:alert(xss)&gt;</code> without using the frontend application at all."
  - `accessLogDisclosureChallenge` - "Gain access to any access log file of the server."
  - `registerAdminChallenge` - "Register as a user with administrator privileges."
  - `adminSectionChallenge` - "Access the administration section of the store."
  - `fileWriteChallenge` - "Overwrite the Legal Information file."
  - `rceChallenge` - "Perform a Remote Code Execution..."
  - `captchaBypassChallenge` - "Submit 10 or more customer feedbacks within 20 seconds."
  - And many more including Web3, NFT, and blockchain challenges

## Impact
Attackers gain complete knowledge of all application challenges, their categories, difficulty levels, and descriptions. This enables targeted exploitation of every challenge, including those that reveal sensitive data exposure, broken authentication, and injection vulnerabilities.

## Risk
High — Complete application challenge catalog exposed without authentication.