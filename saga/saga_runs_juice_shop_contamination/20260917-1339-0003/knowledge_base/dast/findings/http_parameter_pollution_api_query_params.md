## HTTP Parameter Pollution on API Query Parameters

**Endpoint:** GET /api/Challenges/
**Vulnerable Parameters:** key, id, limit, order, sort
**Vulnerability Class:** HTTP Parameter Pollution

### Detection Payloads

1. **Duplicate `key` parameter** — last value wins:
   - Payload: `?key=nftMintChallenge&key=passwordHashLeakChallenge`
   - Response: HTTP 200 returning BOTH challenges (1540 bytes)
   - Baseline `?key=nftMintChallenge` alone returns 1 challenge (987 bytes)

2. **Duplicate `id` parameter** — all values matched:
   - Payload: `?id=1&id=2`
   - Response: HTTP 200 returning challenges with id=1 and id=2

3. **Duplicate `limit` parameter** — last value wins:
   - Payload: `?limit=1&limit=100`
   - Response: HTTP 200 returning ALL 24 challenges (67660 bytes)
   - Baseline without limit returns same full set

4. **Duplicate `order` parameter** — last value wins:
   - Payload: `?sort=createdAt&order=ASC&order=DESC`
   - Response: HTTP 200 returning all challenges

5. **Duplicate `sort` parameter** — causes server error:
   - Payload: `?sort=createdAt&sort=-createdAt`
   - Response: HTTP 500 with `{"message":"internal error","errors":["sortQuery.split is not a function"]}`

6. **Triple `key` parameter**:
   - Payload: `?key=passwordHashLeakChallenge&key=adminSectionChallenge&key=restfulXssChallenge`
   - Response: HTTP 200 returning 3 matching challenges

### Impact
An attacker can manipulate API filtering behavior by supplying duplicate query parameters, potentially bypassing intended pagination, sorting, or filtering logic. The `sort` parameter pollution also leaks internal error details.

### Notes
- The `key` parameter with 3 values (`?key=test&key=1&key=2`) returned empty — behavior is inconsistent across parameter types
- The `sort` parameter with duplicate values causes a server-side JavaScript error rather than a SQL error