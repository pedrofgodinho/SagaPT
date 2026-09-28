# No Reflected XSS in Search Endpoints

- **Vulnerability Class**: Reflected Cross-Site Scripting (XSS) - NOT PRESENT
- **Endpoints Tested**:
  - `GET /rest/products/search?q=`
  - `GET /api/Products?searchTerm=`
- **Payloads Tested**:
  - `<script>alert('XSS')</script>`
  - `"><img src=x onerror=alert(1)>`
  - `<svg/onload=alert(1)>`
- **Result**: No reflected XSS found. Both endpoints return `application/json` responses, which do not echo user input back into the HTML response body. The search query parameter is used server-side for database filtering only.
- **Note**: The `/rest/products/search` endpoint returned a 500 SQL error page when the `<script>` payload was used (SQL injection vector, not XSS). The error page HTML-encodes the payload and does not reflect it unescaped.