## GraphQL Endpoint Non-Functional

**Endpoint:** `POST http://juiceshop.local:3000/graphql`
**Vulnerability Class:** Informational — Endpoint Misconfiguration

### Testing Performed
- Introspection query: `{ __schema { types { name fields { name type { name } } } } }`
- Simple query: `{ __typename }`
- Content types tested: `application/json` (default)

### Evidence
- All POST requests to `/graphql` return **200 OK** with `Content-Type: text/html` and the Angular SPA shell (9393 bytes), NOT a JSON GraphQL response.
- No GraphQL schema introspection data returned.

### Analysis
The GraphQL endpoint is present in the application's route table but is not functional — it returns the default SPA shell for all requests. No GraphQL-specific attacks (introspection, query injection, batch queries) can be performed against it.

### Impact
No direct vulnerability. The endpoint simply does not accept GraphQL queries via HTTP.