# No Reflected XSS in Main SPA Page

- **Vulnerability Class**: Reflected Cross-Site Scripting (XSS) - NOT PRESENT
- **Endpoint**: `GET /` (main page)
- **Payloads Tested**:
  - `GET /?q=<script>alert(1)</script>`
  - `GET /#/<script>alert(1)</script>`
- **Result**: No reflected XSS found. The main page is an Angular SPA that returns static HTML with `<app-root></app-root>` as the only dynamic element. User input from URL parameters is not reflected server-side.