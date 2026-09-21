## Vulnerability: Swagger UI Accessible Without Authentication

**Endpoint:** `/api-docs`
**Parameter:** N/A (path-based)
**Vulnerability Class:** Information Disclosure

### Description
The Swagger UI is accessible at `/api-docs` without authentication, revealing the complete API specification including all endpoints, parameters, and response schemas.

### Evidence
```
GET /api-docs → HTTP 200, Content-Type: text/html
Body contains Swagger UI HTML with embedded API documentation
```

### Impact
Attackers can enumerate all available API endpoints, understand expected parameters and data formats, and identify additional attack surfaces without needing authentication.

### Risk
Medium - API documentation exposure aids reconnaissance and targeted attacks.