## REST API Endpoints Not Accessible via Direct HTTP

**Affected Endpoints:**
- `GET /rest/feedback`
- `POST /rest/feedback`
- `GET /rest/products`
- `GET /api/v1/products`

**Vulnerability Class:** Informational — Application Architecture

### Testing Performed
- GET and POST requests to each endpoint with various content types.

### Evidence
- All requests return **500 Internal Server Error** with body: `Error: Unexpected path: /rest/feedback` (or similar for each endpoint).
- Stack trace shows the error originates from `/juice-shop/build/routes/angular.js:18:18`.

### Analysis
The application is an Angular SPA where REST API endpoints are not defined as server-side Express routes. They are either only accessible through the Angular frontend or not implemented.

### Impact
No vulnerability — these endpoints are simply not exposed via direct HTTP.