# Juice Shop Attack Surface

## Technology Stack
- **Application:** OWASP Juice Shop (deliberately vulnerable web app)
- **Framework:** Express.js ^4.22.1 (Node.js backend)
- **Frontend:** Angular SPA with hash-based routing (/#/...)
- **Database:** SQLite (inferred from Juice Shop defaults)
- **Authentication:** JWT-based (Bearer token in Authorization header)
- **CORS:** Wildcard `Access-Control-Allow-Origin: *`

## Discovered Endpoints

### Public API Endpoints (No Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all products (returns JSON array) |
| GET | `/api/securityQuestions` | List all security questions (14 questions) |

### User Registration
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users` | User registration (JSON body) |

### Auth-Required API Endpoints (Bearer token needed)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users (requires auth) |
| GET | `/api/users/25` | Get user by ID (requires auth) |
| GET | `/api/users/current` | Get current user profile (requires auth) |

### SPA Hash Routes (Angular frontend)
| Route | Description |
|-------|-------------|
| `/#/` | Homepage |
| `/#/login` | Login page |
| `/#/signup` | Registration page |
| `/#/jobs` | Jobs/careers page (referenced in X-Recruiting header) |

### Static Files & Assets
| Path | Description |
|------|-------------|
| `/styles.css` | Main stylesheet |
| `/scripts.js` | JavaScript bundle |
| `/main.js` | Angular main bundle |
| `/polyfills.js` | Browser polyfills |
| `/assets/public/favicon_js.ico` | Favicon |

### FTP Directory (Exposed File Server)
| Path | Description |
|------|-------------|
| `/ftp/` | Directory listing |
| `/ftp/acquisitions.md` | Confidential acquisition plans |
| `/ftp/legal.md` | Legal information |
| `/ftp/announcement_encrypted.md` | Encrypted announcement |
| `/ftp/coupons_2013.md.bak` | Backup file (403 - only .md/.pdf allowed) |
| `/ftp/eastere.gg` | Easter egg file |
| `/ftp/encrypt.pyc` | Python compiled file |
| `/ftp/incident-support.kdbx` | KeePass database |
| `/ftp/package-lock.json.bak` | Package lock backup |
| `/ftp/package.json.bak` | Package JSON backup |
| `/ftp/quarantine/` | Quarantine directory with malware URL files |

### Other
| Path | Description |
|------|-------------|
| `/robots.txt` | Disallows `/ftp` |
| `/sitemap.xml` | Returns SPA HTML (not actual sitemap) |

## Input Points

### 1. User Registration (POST /api/users)
- **Content-Type:** `application/json`
- **Fields:**
  - `email` (string, required)
  - `password` (string, required)
  - `nickname` (string)
  - `securityQuestion.id` (integer, question ID 1-14)
  - `securityQuestion.answer` (string)
  - `remember` (boolean)

### 2. Login (Form-based via SPA)
- **Route:** `/#/login` (Angular SPA)
- **Fields:** `email`, `password`
- **Auth mechanism:** JWT Bearer token stored in cookie/localStorage

### 3. Security Questions
- **GET /api/securityQuestions** - Returns 14 questions (IDs 1-14):
  1. Your eldest siblings middle name?
  2. Mother's maiden name?
  3. Mother's birth date? (MM/DD/YY)
  4. Father's birth date? (MM/DD/YY)
  5. Maternal grandmother's first name?
  6. Paternal grandmother's first name?
  7. Name of your favorite pet?
  8. Last name of dentist when you were a teenager?
  9. Your ZIP/postal code when you were a teenager?
  10. Company you first work for as an adult?
  11. Your favorite book?
  12. Your favorite movie?
  13. Number of one of your customer or ID cards?
  14. What's your favorite place to go hiking?

### 4. File Upload/Download (FTP)
- **Path:** `/ftp/` - Directory listing with file downloads
- **Constraint:** Only `.md` and `.pdf` files allowed (enforced by server)
- **Input:** File path in URL path

### 5. URL Parameters (inferred from SPA)
- Hash-based routing: `/#/product/1`, `/#/product/2`, etc. (product IDs)
- `/#/about`, `/#/contact`, `/#/recycle` (referenced in product descriptions)
- `/#/admin` (likely admin panel)
- `/#/admin/users` (likely user management)
- `/#/admin/configuration` (likely config)
- `/#/admin/leaderboard` (likely leaderboard)
- `/#/admin/feedback` (likely feedback management)
- `/#/admin/orders` (likely order management)
- `/#/admin/security` (likely security settings)

### 6. HTTP Headers
- **Authorization:** Bearer token for authenticated requests
- **Content-Type:** `application/json` for API POSTs
- **Custom header:** `X-Recruiting: /#/jobs` (from homepage)

### 7. Cookies
- Cookie consent cookie (cookieconsent)
- Session/auth cookies (JWT-based)

## Security Observations
- **CORS:** Wildcard `*` allows any origin
- **CSP:** Not set on any response
- **Timestamps:** Unix timestamps disclosed in CSS file
- **Error disclosure:** Stack traces visible on 500 errors
- **Sensitive files:** FTP directory exposes confidential documents, encrypted files, backups
- **Default credentials:** Juice Shop ships with default admin account (admin@juiceshop.sh / admin)
- **Product prices:** Can be manipulated (e.g., O-Saft at $0.01, Snakes & Ladders at $0.01)
- **Deluxe pricing:** Some products have discounted deluxe prices

## Test Credentials Created
- **Email:** test@example.com
- **Password:** Test1234!
- **User ID:** 25 (created via POST /api/users)
