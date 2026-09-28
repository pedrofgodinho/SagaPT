# B2B API Endpoint Requires Authentication

## Endpoint
- **POST** `/b2b/v2/orders`

## Test Results
- **Without auth**: Returns `401 UnauthorizedError: No Authorization header was found`
- The endpoint is properly protected and requires JWT bearer authentication
- Attempting to POST with a simple JSON body `{"cid":"1","orderLines":[{"product":1,"quantity":1}]}` without auth returns 401
- Attempting SQLi in body `{"cid":"1' OR '1'='1",...}` also returns 401 (auth blocks first)

## Conclusion
The B2B API endpoint is properly secured with JWT authentication. Without valid credentials, the endpoint is inaccessible. This is correct behavior.