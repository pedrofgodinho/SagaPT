## Search and Profile Endpoints - Not Accessible via REST

- **Endpoints Tested:**
  - GET /rest/search?q=test
  - GET /rest/products
  - GET /rest/users/256
  - GET /rest/user/profile
- **Evidence:** All returned 500 "Unexpected path" errors from Angular SPA router (`/juice-shop/build/routes/angular.js:18:18`).
- **Assessment:** These endpoints are not accessible via REST API. The application uses Angular hash-based routing (`/#/`) for all client-side navigation, and REST endpoints are caught by the SPA router before reaching application logic.
- **Impact:** SQL Injection and XSS testing on search query and profile fields could not be performed because these endpoints do not exist as accessible REST APIs.