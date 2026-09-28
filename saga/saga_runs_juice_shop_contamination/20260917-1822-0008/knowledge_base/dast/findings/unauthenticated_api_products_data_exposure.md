## Unauthenticated Access to /api/Products Exposing All Product Data

- **Endpoint:** GET http://juiceshop.local:3000/api/Products
- **Vulnerability Class:** Broken Access Control / Information Disclosure
- **Detection Payload:** GET /api/Products with no authentication
- **Evidence:** HTTP 200 with full JSON response containing all products unauthenticated. Response includes product IDs, names, descriptions (with embedded HTML links), prices, deluxe prices, image filenames, creation/update timestamps, and deletedAt status. All 30+ products accessible without auth.
- **Impact:** Unauthenticated users can enumerate all products, prices, and metadata. While products are likely intended to be public, this confirms the API has no authentication requirement and could expose additional sensitive fields if added.
- **Priority:** LOW - product catalog is typically public, but confirms lack of API auth enforcement.