# SQL Injection in /api/Products Search Parameter

## Endpoint
- **GET** `/api/Products?search=' OR '1'='1`

## Test Results
- **Status**: 200 OK
- **Response**: Returns ALL products in the database (35+ items), not filtered by search term
- The SQL injection payload `' OR '1'='1` was injected into the search parameter
- Expected: Only products matching the search term should be returned
- Actual: All products returned regardless of search term - indicates the WHERE clause is being bypassed

## Evidence
The response body contains all products (Apple Juice, Orange Juice, Eggfruit Juice, Raspberry Juice, etc.) - the search filter was completely bypassed by the SQL injection.

## Impact
- **Confidentiality**: Can enumerate all products in the database
- **Data Exfiltration**: Potentially can extract data from other tables via UNION-based injection
- This is a confirmed SQL injection vulnerability in the Products search endpoint

## Recommendation
- Use parameterized queries/prepared statements for all database queries
- Validate and sanitize all user input
- Implement proper input validation on the search parameter