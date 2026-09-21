## Sort Parameter Reflects User Input in JSON Error Responses

**Vulnerability Class:** Input Reflection (JSON context, not HTML XSS)
**Endpoint:** GET /api/Products
**Vulnerable Parameter:** sort
**Detection Payload:** sort=<script>alert(1)</script>
**Evidence:**
- Request: GET http://juiceshop.local:3000/api/Products?sort=<script>alert(1)</script>
- Response: HTTP 400 with body: `{"message":"Sorting not allowed on given attributes","errors":["<script>alert(1)</script>"]}`
- The input is reflected verbatim in the `errors` array of the JSON response
- Response Content-Type is `application/json`, so this is NOT exploitable as reflected XSS

**Additional observations:**
- The sort parameter validates against a whitelist of allowed attributes
- Invalid sort values (including XSS payloads, JSON objects, MongoDB operators) are rejected with 400
- The `costPrice` field is NOT a valid sort attribute (returns 400), confirming it is not exposed in the API
- The `limit` parameter is not enforced (returns all products regardless of value)
- Valid sort values like `name`, `price`, `id` work correctly

**Conclusion:** While the sort parameter reflects user input in error messages, this occurs in JSON context only and cannot be leveraged for XSS. The input validation (whitelist check) is functioning correctly.