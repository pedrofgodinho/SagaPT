# Attack Surface — OWASP Juice Shop (http://juiceshop.local:3000)

## Technology Stack
- **Backend**: Node.js + Express ^4.22.1
- **Frontend**: Angular SPA (Material Design components)
- **Auth**: JWT (RS256), Bearer token in Authorization header
- **ORM**: Sequelize (SQLite implied)
- **Build**: Rollup/Rolldown (chunked JS bundles)
- **CORS**: `Access-Control-Allow-Origin: *` (wildcard)
- **Security headers**: X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Feature-Policy: payment 'self'
- **Missing**: CSP header, Strict-Transport-Security

---

## API Endpoints Discovered

### `/api/` Endpoints

| Method | Path | Auth Required | Notes |
|--------|------|--------------|-------|
| GET | `/api/Users` | Yes (401 w/o token) | Returns user list |
| POST | `/api/Users` | No | User registration — accepts JSON body |
| GET | `/api/Products` | No | Returns all products (200) |
| GET | `/api/BasketItems` | Yes (401) | Returns basket items |
| POST | `/api/BasketItems` | Likely | Add items to basket |
| GET | `/api/Feedbacks` | No | Returns feedback list (200) |
| POST | `/api/Feedbacks` | Likely | Submit feedback |
| DELETE | `/api/Feedbacks/{id}` | Likely | Delete feedback |
| GET | `/api/Complaints` | Yes (401) | Returns complaints |
| GET | `/api/SecurityQuestions` | No | Returns 14 security questions (200) |
| GET | `/api/Challenges/?key=` | Likely | Challenges API with `key` query param |
| GET | `/api/Orders` | Unknown | 500 error on GET (unexpected path) |
| GET | `/api/Coupons` | Unknown | 500 error on GET (unexpected path) |

### `/rest/` Endpoints

| Method | Path | Auth Required | Notes |
|--------|------|--------------|-------|
| POST | `/rest/user/login` | No | Login — form body with email/password, returns JWT |
| GET | `/rest/products/search?q=` | No | Product search — `q` query param |
| GET | `/rest/web3/nftUnlocked` | No | NFT status check |
| GET | `/rest/web3/nftMintListen` | No | NFT mint listener |
| POST | `/rest/web3/submitKey` | Likely | Submit private key |
| POST | `/rest/web3/walletNFTVerify` | Likely | Verify NFT wallet |
| POST | `/rest/web3/walletExploitAddress` | Likely | Exploit wallet address |

### Static / File Endpoints

| Method | Path | Notes |
|--------|------|-------|
| GET | `/main.js` | Angular app bundle (~1.2 MB) |
| GET | `/polyfills.js` | Browser polyfills |
| GET | `/scripts.js` | App scripts |
| GET | `/styles.css` | Global styles |
| GET | `/assets/public/` | Public assets (images, icons) |
| GET | `/sitemap.xml` | Site map (HTML, not XML — XSS risk) |
| GET | `/robots.txt` | Disallows `/ftp` |

### FTP / Exposed Files

| Method | Path | Notes |
|--------|------|-------|
| GET | `/ftp/` | Directory listing |
| GET | `/ftp/package.json.bak` | Backup file |
| GET | `/ftp/package-lock.json.bak` | Backup file |
| GET | `/ftp/incident-support.kdbx` | KeePass database |
| GET | `/ftp/eastere.gg` | Easter egg file |
| GET | `/ftp/suspicious_errors.yml` | Error config |
| GET | `/ftp/acquisitions.md` | Markdown doc |
| GET | `/ftp/encrypt.pyc` | Python bytecode |
| GET | `/ftp/announcement_encrypted.md` | Encrypted announcement |
| GET | `/ftp/legal.md` | Legal doc |
| GET | `/ftp/coupons_2013.md.bak` | Old coupons backup |
| GET | `/ftp/quarantine/` | Quarantine directory |

### SPA Routes (Angular hash-based)

| Path | Notes |
|------|-------|
| `/#/jobs` | Referenced in X-Recruiting header |
| `/#/` | Home page |

---

## Input Parameters

### Query Parameters
- `q` — on `GET /rest/products/search?q=` — product search query
- `key` — on `GET /api/Challenges/?key=` — challenge filter

### URL Path Parameters
- `{id}` — on `/api/Users/{id}`, `/api/Products/{id}`, `/api/Feedbacks/{id}`, `/api/BasketItems/{id}`, `/api/Complaints/{id}`, `/api/Orders/{id}`

### POST Body — JSON (`Content-Type: application/json`)
- **`POST /api/Users`**: `email`, `password`, `username`, `languageCode`
- **`POST /rest/web3/submitKey`**: `privateKey`
- **`POST /rest/web3/walletNFTVerify`**: `walletAddress`
- **`POST /rest/web3/walletExploitAddress`**: `walletAddress`

### POST Body — Form (`Content-Type: application/x-www-form-urlencoded`)
- **`POST /rest/user/login`**: `email`, `password`

### Headers
- `Authorization: Bearer <jwt>` — for authenticated endpoints

---

## Authentication Details
- **Registration**: `POST /api/Users` — no auth required, no rate limiting observed
- **Login**: `POST /rest/user/login` — form-encoded `email` + `password`
- **Token format**: JWT with RS256 algorithm, returned as `authentication.token` in JSON response
- **Token payload includes**: user id, username, email, role, deluxeToken, lastLoginIp, profileImage, totSecret, isActive, createdAt, updatedAt
- **Additional response fields**: `bid` (basket id), `umail` (user email)

---

## Security Observations (Informational)
1. Wildcard CORS (`Access-Control-Allow-Origin: *`)
2. No CSP header set
3. Timestamp disclosure in CSS files
4. Application error disclosure (stack traces on 500 errors)
5. Unauthenticated user registration
6. Security questions publicly accessible via `/api/SecurityQuestions`
7. FTP directory with sensitive backup files exposed
8. Sitemap returns HTML instead of XML (potential XSS vector)
9. X-Recruiting header points to `/#/jobs` (information disclosure)
10. Angular Material Design components in use (MDC-based theming)
