# Products API by ID Endpoint

## Vulnerability Class
Information Disclosure

## Endpoint
`GET /api/products/{id}`

## Evidence
- `GET /api/products/1` returns:
  ```json
  {"status":"success","data":{"id":1,"name":"Apple Juice (1000ml)","description":"The all-time classic.","price":1.99,"deluxePrice":0.99,"image":"apple_juice.jpg","createdAt":"2026-09-17T08:56:43.424Z","updatedAt":"2026-09-17T08:56:43.424Z","deletedAt":null}}
  ```
- `GET /api/products/999999` returns 404: `{"message":"Not Found","errors":[]}`

## Impact
Products can be retrieved by numeric ID. This could be used for enumeration of product IDs.

## Risk
Low — Information disclosure through ID enumeration.