# Public Challenges Endpoint Disclosure

## Vulnerability Class
Information Disclosure / Sensitive Data Exposure

## Endpoint
`GET /api/challenges`

## Evidence
- Unauthenticated GET to `/api/challenges` returns HTTP 200 with full JSON array of all 17+ challenges
- Response includes: challenge IDs, keys, names, categories, difficulty levels, descriptions, tags, dependencies, and solved status
- Sample response data:
  ```json
  {
    "status": "success",
    "data": [
      {
        "id": 1,
        "key": "passwordHashLeakChallenge",
        "name": "Password Hash Leak",
        "category": "Sensitive Data Exposure",
        "difficulty": 2,
        "description": "Obtain the password (hash) of the currently logged-in user directly from a REST API endpoint.",
        "solved": false
      },
      ...
    ]
  }
  ```

## Impact
Attackers gain complete knowledge of all application challenges, their categories, difficulty levels, and descriptions. This enables targeted attacks on specific challenges and reveals the application's security architecture.

## Risk
Medium — Reveals complete challenge taxonomy and attack surface.

## Recommendation
Require authentication for accessing challenge metadata endpoints.