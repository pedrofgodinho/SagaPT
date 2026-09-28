## Registration Endpoints - Not Accessible

- **Endpoints Tested:** POST /rest/user/registration, POST /rest/user/register, POST /rest/user/signup
- **Payloads Tested:** `' trash` (SQLi probe), `<script>alert(1)</script>` (XSS probe)
- **Evidence:** All registration paths returned 500 "Unexpected path: /rest/user/registration" (or similar) for both JSON and form-encoded POSTs. The error originates from `/juice-shop/build/routes/angular.js:18:18` — the Angular SPA router is catching these paths before they reach application logic.
- **Assessment:** These endpoints are not accessible via REST API. The application appears to handle registration client-side through Angular routing, not server-side REST endpoints. SQLi and XSS testing could not be performed because the input never reaches application logic.
- **Note:** This is a configuration/routing issue, not a vulnerability. The registration functionality may be handled through a different mechanism (e.g., the Angular frontend calling a different internal endpoint).