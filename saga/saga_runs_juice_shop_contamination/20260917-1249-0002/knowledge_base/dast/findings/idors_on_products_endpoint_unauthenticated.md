# IDOR on /api/products Endpoint - Unauthenticated Access

- **Endpoint:** GET /api/products/{id}
- **Vulnerable Parameter:** Path parameter `id`
- **Detection Payload:** GET /api/products/1, /api/products/2, /api/products/3, /api/products/4, /api/products/5
- **Evidence:** All requests return 200 OK with product data (name, description, price, deluxePrice, image, etc.) without any authentication. Multiple product IDs tested successfully.
- **Impact:** Any unauthenticated user can enumerate and access all product data by simply incrementing the ID parameter. Prices and deluxePrices are exposed.
- **Risk:** Medium - Product catalog enumeration without authentication