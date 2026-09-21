## Sensitive Data Exposure via Challenge List Endpoint

**Endpoint:** GET /api/Challenges (and /api/Challenges/)
**Vulnerability Class:** Sensitive Data Exposure (Excessive Data Exposure)

### Detection Payload
- `GET /api/Challenges`
- Response: HTTP 200 with full JSON array of all challenges (67KB+ response)

### Evidence
The endpoint returns the complete list of all application challenges including:
- Challenge IDs, keys, names, categories, and descriptions
- Difficulty ratings (1-6)
- Tags and mitigation URLs
- Challenge dependencies and coding challenge status
- Creation/update timestamps
- Tutorial order information

This reveals the application's security challenge architecture, including:
- "Password Hash Leak" - Sensitive Data Exposure
- "Admin Section" - Broken Access Control
- "CAPTCHA Bypass" - Broken Anti Automation
- "Blocked RCE DoS" - Insecure Deserialization
- "Access Log" - Observability Failures
- "Web3 Sandbox" - Broken Access Control
- And 12+ other challenges with full descriptions

### Impact
Attackers can:
- Map the application's security controls and their weaknesses
- Identify high-value targets (difficulty 5-6 challenges)
- Understand the application's security architecture
- Prioritize exploitation based on challenge descriptions and tags

### Notes
This endpoint is publicly accessible without authentication. The response is identical whether accessed with or without query parameters.