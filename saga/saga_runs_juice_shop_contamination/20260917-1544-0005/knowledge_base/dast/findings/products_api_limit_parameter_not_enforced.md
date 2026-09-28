## Products API - Limit Parameter Not Enforced

**Vulnerability Class:** Excessive Data Exposure / Broken Access Control
**Endpoint:** GET /api/Products
**Vulnerable Parameter:** limit
**Evidence:**
- Request: GET http://juiceshop.local:3000/api/Products?limit=1
- Response: HTTP 200 with ALL 30+ products returned (not just 1)
- Response body length: 16011 bytes (same as unfiltered request)
- All product data returned: id, name, description, price, deluxePrice, image, createdAt, updatedAt, deletedAt
- The limit parameter appears to be ignored by the backend

Comparison:
- GET /api/Products (no limit) returns the same full dataset
- GET /api/Products?limit=' (SQL injection probe) also returns full dataset
- The `limit` parameter does not restrict the number of results

**Impact:** API pagination parameters are not enforced, allowing clients to potentially bypass intended rate limiting or pagination controls. All product data is returned regardless of client request.

**Detection Payload:** GET /api/Products?limit=1 - received all 30+ products instead of 1