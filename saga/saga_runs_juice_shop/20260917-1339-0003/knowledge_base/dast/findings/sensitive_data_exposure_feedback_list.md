## Sensitive Data Exposure via Feedback List Endpoint

**Endpoint:** GET /api/Feedbacks (and /api/Feedbacks/)
**Vulnerability Class:** Sensitive Data Exposure (Excessive Data Exposure)

### Detection Payload
- `GET /api/Feedbacks`
- Response: HTTP 200 with full JSON array of all customer feedbacks

### Evidence
The endpoint returns all customer feedbacks including:
- User IDs (UserId field: 1, 2, 3, 21)
- Feedback IDs (1-8)
- Full comment text including HTML content
- Ratings (1-5)
- Creation/update timestamps
- Partial email addresses (e.g., ***in@juice-sh.op, ***@juice-sh.op)

Notable data exposed:
- Feedback #4 contains a seed phrase: "purpose betray marriage blame crunch monitor spin slide donate sport lift clutch" associated with a wallet
- Feedbacks contain HTML tags (<br />, <em>, <b>) suggesting insufficient output encoding
- User IDs are sequential, enabling enumeration of other users

### Impact
Attackers can:
- Enumerate user accounts by UserId
- Access sensitive data stored in feedbacks (seed phrases, personal info)
- Identify high-value targets for further attacks
- Correlate user IDs with other data in the application

### Notes
This endpoint is publicly accessible without authentication. Individual feedback access (/api/Feedbacks/1) requires authentication (401).