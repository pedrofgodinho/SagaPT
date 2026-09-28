## Angular SPA Admin Route Accessible Without Authentication

- **Endpoint:** GET http://juiceshop.local:3000/#/admin
- **Vulnerability Class:** Broken Access Control
- **Detection Payload:** GET /#/admin with no authentication
- **Evidence:** HTTP 200 returned for the admin route without any authentication. The Angular SPA routes are client-side only, and the server returns the same HTML shell for all routes regardless of access level. The `/#/admin` path is accessible to unauthenticated users.
- **Impact:** While the server-side API still requires authentication (confirmed by 401 on /api/Feedbacks/1), the client-side admin interface is accessible without auth. An attacker can load the admin UI and then attempt to interact with protected API endpoints. The absence of server-side route protection means the admin interface is discoverable and loadable by anyone.
- **Priority:** MEDIUM - client-side access control bypass; server-side APIs still require auth but the admin UI exposure aids reconnaissance.