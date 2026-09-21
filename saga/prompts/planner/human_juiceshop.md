Your target is {target}. You have access to the recon agent, the DAST agent, and the exploitation agent. This target is OWASP Juice Shop, a deliberately vulnerable modern single-page application (Node.js/Express/Angular). It exposes a REST API under `/api/` and `/rest/` and serves its Angular frontend from the root. There is no separate setup step — the application is ready to test immediately.

Important implementation notes for this target:
- The application is an Angular SPA; most functionality is driven by REST API calls, not traditional HTML form submissions. The recon agent should focus on discovering API endpoints (examine JavaScript sources and network traffic), not just HTML pages.
- Authentication uses JWT tokens via the `/rest/user/login` endpoint (POST with JSON body containing `email` and `password`). The token is returned in the response body, not set as a cookie.
- The search functionality is at `/rest/products/search?q=` (not a traditional HTML form).
- User registration is at `POST /api/Users` (JSON body with `email`, `password`, `passwordRepeat`).
- The `/api/` endpoints follow a REST pattern: `/api/Products`, `/api/Users`, `/api/BasketItems`, `/api/Feedbacks`, `/api/Complaints`, etc.

Your objectives, in priority order:
1. Use the recon agent to explore the application: discover API endpoints, identify the technology stack, enumerate input points, and register a test account (e.g. email: "test@test.com", password: "testtest123").
2. Use the DAST agent to test for SQL injection on every endpoint and parameter recon identifies — do not stop after the first one is found. The search endpoint (`/rest/products/search?q=`) is a known injection point.
3. For each confirmed vulnerability, use the exploitation agent to demonstrate impact (e.g. extract data, escalate privileges).
