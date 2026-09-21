# Technology Stack - OWASP Juice Shop

## Server-Side
- **Runtime:** Node.js
- **Framework:** Express.js ^4.22.1
- **Application:** OWASP Juice Shop (Björn Kimminich)
- **License:** MIT

## Client-Side
- **Framework:** Angular (SPA with hash-based routing)
- **UI Library:** Angular Material (bluegrey-lightgreen-theme)
- **Fonts:** VT323 (Google Fonts), Roboto
- **Build:** Angular CLI (main.js, polyfills.js, scripts.js bundles)

## API Architecture
- **REST API:** `/api/` base path
- **GraphQL:** `/graphql` endpoint (Angular SPA routing fallback)
- **Authentication:** JWT-based via `Authorization` header
- **CORS:** Wildcard `Access-Control-Allow-Origin: *`

## Data Storage
- **ORM:** Sequelize (evidenced by `createdAt`, `updatedAt`, `deletedAt` fields)
- **Database:** Likely SQLite or PostgreSQL (Juice Shop default)

## Notable Configuration
- **robots.txt:** Disallows `/ftp` path
- **sitemap.xml:** Returns HTML (SPA, not XML sitemap)
- **File Server:** Static file serving enabled at root and `/assets/public/`
- **FTP Directory:** Publicly browsable at `/ftp/` with file download