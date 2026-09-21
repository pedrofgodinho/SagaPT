## Timestamp Disclosure in API Responses

**Endpoints Affected:**
- GET /api/SecurityQuestions
- GET /api/Products
- GET /api/Products?search=%27+trash
- GET /api/Products?minPrice=%27+trash

**Vulnerability Class:** Information Disclosure

### Detection

API responses include `createdAt`, `updatedAt`, and `deletedAt` timestamps in ISO 8601 format, as well as Unix timestamps in response headers and body data.

### Evidence

Request: `GET /api/SecurityQuestions`
Response body includes timestamps:
```json
{"id":1,"question":"Your eldest siblings middle name?","createdAt":"2026-09-17T11:48:32.490Z","updatedAt":"2026-09-17T11:48:32.490Z"}
```

ZAP Alert: `Timestamp Disclosure - Unix` detected on `GET /api/Products?search=%27+trash` and `GET /api/Products?minPrice=%27+trash` with evidence values like `1969196030` and `1970691216` (Steam Workshop IDs embedded in product descriptions).

### Impact

- Timestamps can reveal application lifecycle information (when records were created/updated/deleted)
- Unix timestamps in product descriptions (Steam Workshop IDs) leak third-party service references
- Combined with other data, timestamps can help an attacker profile user activity patterns

### Recommendation

Consider removing or obfuscating timestamps from API responses where they are not required by the client. Do not include third-party service identifiers or references in product data.