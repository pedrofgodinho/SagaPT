## HTTP Methods PUT/DELETE/PATCH Not Testable

**Endpoint:** Various endpoints
**Vulnerability Class:** Tool Limitation

### Testing Performed
- Attempted to test PUT, DELETE, PATCH methods via `http_post` tool
- The `http_post` tool only sends HTTP POST requests, not PUT/DELETE/PATCH

### Evidence
- `http_post` tool with `content_type="json"` sends POST with Content-Type: application/json
- `http_post` tool with `content_type="form"` sends POST with Content-Type: application/x-www-form-urlencoded
- No tool available to send PUT, DELETE, or PATCH requests

### Analysis
The scanning toolset does not support sending PUT, DELETE, or PATCH HTTP methods. These methods cannot be tested for exposure or access control issues.

### Recommendation
Use a tool that supports arbitrary HTTP methods (e.g., curl, Postman, or a DAST tool with full HTTP method support) to test:
- Whether PUT/DELETE/PATCH are accepted on any endpoints
- Whether these methods bypass access controls
- Whether they modify data on the server