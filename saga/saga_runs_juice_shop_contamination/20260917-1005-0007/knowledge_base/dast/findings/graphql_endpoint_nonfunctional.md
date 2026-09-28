# GraphQL Endpoint Non-Functional

## Vulnerability Class
Non-functional / Misconfigured Endpoint (Informational)

## Endpoint Tested
- `POST http://juiceshop.local:3000/graphql`
- `POST http://juiceshop.local:3000/api/graphql`
- `POST http://juiceshop.local:3000/juice-shop/graphql`
- `GET http://juiceshop.local:3000/graphql?query={__typename}`

## Evidence

### POST /graphql (6 queries tested)
All returned the Angular SPA shell (9393 bytes, `Content-Type: text/html`, status 200):
- `{"query":"{__typename}"}` → Angular shell
- `{"query":"{securityQuestion(userEmail: \"test@test.com\")}"}` → Angular shell
- `{"query":"{users {id email password}}"}` → Angular shell
- `{"query":"{products {id name price}}"}` → Angular shell
- `{"query":"{orders {id}}"}` → Angular shell
- `{"query":"{challenge(key: \"test\")}"}` → Angular shell
- `{"query":"{__schema {types {name fields {name type {name}}}}}"}` (introspection) → Angular shell

### POST /api/graphql
Returned HTTP 500 with Express error:
```
Error: Unexpected path: /api/graphql
Stack trace shows: /juice-shop/build/routes/angular.js:18:18
```

### POST /juice-shop/graphql
Angular shell (200, HTML)

### GET /graphql?query={__typename}
Angular shell (200, HTML)

## Conclusion
The GraphQL endpoint at `/graphql` is **not functional** as a GraphQL API. The application routes all unrecognized paths to the Angular SPA shell (catch-all route). The `/api/graphql` path exists but returns a 500 error indicating the route is not configured.

Since no GraphQL endpoint is functional, the following vulnerability classes are **not applicable** to this target:
- **SQL Injection via GraphQL**: Cannot test against a non-functional GraphQL endpoint
- **Reflected XSS via GraphQL**: Cannot test against a non-functional GraphQL endpoint
- **GraphQL Introspection**: Not available (no GraphQL schema exposed)

## Impact
Low — The GraphQL endpoint is not exposed/functional, so there is no attack surface via GraphQL. The Angular SPA is served as a fallback for unrecognized routes.

## Recon Alignment
This confirms the recon agent's finding that "POST /graphql returned the Angular shell (not functional GraphQL)."