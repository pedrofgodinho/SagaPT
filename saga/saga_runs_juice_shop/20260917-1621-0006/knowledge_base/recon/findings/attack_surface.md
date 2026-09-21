# OWASP Juice Shop - Attack Surface Map

## Technology Stack
- **Frontend:** Angular (SPA with client-side routing via `#/` hash fragments)
- **Backend:** Node.js + Express ^4.22.1
- **Database:** SQLite (implied by Juice Shop defaults)
- **Authentication:** JWT-based (Authorization header required for protected endpoints)
- **CORS:** `Access-Control-Allow-Origin: *` (wildcard)
- **Security Headers:** X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Feature-Policy: payment 'self'
- **Missing:** Content Security Policy (CSP) header

## Discovered Endpoints and Input Points

### Public API Endpoints (No Auth Required)
| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/Products` | GET | 200 | Returns full product catalog (JSON). Fields: id, name, description, price, deluxePrice, image, createdAt, updatedAt, deletedAt |
| `/api/SecurityQuestions` | GET | 200 | Returns list of 14 security questions. Fields: id, question, createdAt, updatedAt |
| `/api/Products/{id}` | GET | ? | Product detail endpoint (unconfirmed) |
| `/robots.txt` | GET | 200 | Disallows `/ftp` |
| `/sitemap.xml` | GET | 200 | Returns main page HTML (SPA) |

### Authenticated API Endpoints (Require Authorization Header)
| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/Users` | GET | 401 | Requires JWT token |
| `/api/PrivacyRequests` | GET | 401 | Requires JWT token |
| `/api/Me` | GET | 500 | Unexpected path (may need different route) |

### Potential/Unconfirmed API Endpoints
| Endpoint | Method | Notes |
|----------|--------|-------|
| `/api/Basket` | GET/POST/PUT/DELETE | Cart functionality |
| `/api/Cart` | GET/POST/PUT/DELETE | Alternative cart endpoint |
| `/api/Order` | GET/POST | Order management |
| `/api/Feedback` | POST | User feedback submission |
| `/api/Coupons` | GET/POST | Coupon management |
| `/api/Complaint` | POST | Complaint submission |
| `/api/SupportTickets` | GET/POST | Support ticket system |
| `/api/Delivery` | GET/POST | Delivery methods |
| `/api/Cipher` | GET/POST | Cipher functionality |
| `/api/Recycle` | POST | Recycling returns |
| `/api/SecurityQuestions/{id}` | GET | Individual security question |

### Authentication Endpoints (SPA-based)
| Endpoint | Method | Notes |
|----------|--------|-------|
| `/#/login` | GET | Login page (Angular SPA route) |
| `/#/signup` | GET | Registration page (Angular SPA route) |
| `/#/jobs` | GET | Jobs page (referenced in X-Recruiting header) |

### Authentication POST Endpoints (to be determined exact route)
| Endpoint | Method | Input Fields |
|----------|--------|-------------|
| `/api/auth/login` | POST | email, password |
| `/api/auth/signup` | POST | name, email, password, passwordVerification |

### File System / FTP Directory
| Path | Method | Status | Notes |
|------|--------|--------|-------|
| `/ftp/` | GET | 200 | Directory listing (Express serve-index) |
| `/ftp/acquisitions.md` | GET | 200 | Confidential acquisition plans |
| `/ftp/announcement_encrypted.md` | GET | 200 | Encrypted announcement (369KB) |
| `/ftp/coupons_2013.md.bak` | GET | ? | Backup file with coupons |
| `/ftp/eastere.gg` | GET | ? | Easter egg file |
| `/ftp/encrypt.pyc` | GET | 403 | Python bytecode (only .md/.pdf allowed) |
| `/ftp/incident-support.kdbx` | GET | ? | KeePass database |
| `/ftp/legal.md` | GET | ? | Legal documents |
| `/ftp/package-lock.json.bak` | GET | ? | NPM package backup |
| `/ftp/package.json.bak` | GET | ? | NPM package backup |
| `/ftp/quarantine/` | GET | ? | Quarantine directory |
| `/ftp/quarantine/juicy_malware_macos_64.url` | GET | ? | Malware URL file |
| `/ftp/quarantine/juicy_malware_linux_amd_64.url` | GET | ? | Malware URL file |
| `/ftp/quarantine/juicy_malware_linux_arm_64.url` | GET | ? | Malware URL file |
| `/ftp/quarantine/juicy_malware_windows_64.exe.url` | GET | ? | Malware URL file |
| `/ftp/suspicious_errors.yml` | GET | 403 | YAML config (only .md/.pdf allowed) |
| `/ftp/` (directory traversal) | GET | ? | File download endpoint with extension validation |

### Static Assets
| Path | Method | Notes |
|------|--------|-------|
| `/main.js` | GET | Main Angular bundle (~1.2MB) |
| `/scripts.js` | GET | Application scripts |
| `/polyfills.js` | GET | Angular polyfills |
| `/styles.css` | GET | Stylesheet with timestamp data |
| `/assets/public/favicon_js.ico` | GET | Favicon |

### Error/Debug Endpoints (Application Error Disclosure)
| Path | Method | Notes |
|------|--------|-------|
| `/api/v1/*` | GET | All return 500 with stack traces |
| `/rest/SecurityQuestions` | GET | Returns 500 error |
| `/rest/auth/login` | GET | Returns 500 error |

## Input Points Summary

### Query Parameters
- Product search/filter (via SPA, not directly observable)

### Form Fields (SPA-based)
- **Login:** email, password
- **Signup:** name, email, password, passwordVerification
- **Feedback:** message, email (likely)
- **Complaint:** description, details (likely)
- **Support Tickets:** subject, description (likely)

### API Input Points
- **POST /api/auth/signup:** name, email, password, passwordVerification
- **POST /api/auth/login:** email, password
- **POST /api/Feedback:** message, email
- **POST /api/Complaint:** description, details
- **POST /api/Order:** product id, quantity, delivery method, payment info
- **POST /api/Basket:** product id, quantity
- **POST /api/Recycle:** product id, order ID
- **POST /api/SupportTickets:** subject, description, priority

### Headers
- **Authorization:** Bearer token required for protected endpoints
- **X-Recruiting:** `/#/jobs` (custom header)

### URL Parameters
- Product ID: `/api/Products/{id}`
- Security Question ID: `/api/SecurityQuestions/{id}`
- User ID: `/api/Users/{id}`

### File Upload/Download
- FTP file download with extension validation (only .md and .pdf allowed)
- Extension bypass potential (403 on .pyc, .kdbx, .yml, .gg, .bak)

## User Roles
- **Anonymous:** Access to Products, SecurityQuestions, FTP (partial), static assets
- **Authenticated User:** Access to Basket, Orders, PrivacyRequests, Me, Feedback, Complaints, SupportTickets
- **Admin:** Access to Users management (implied)
- **Security Questions:** 14 questions available for account recovery

## Security Observations
1. Wildcard CORS (`Access-Control-Allow-Origin: *`)
2. No Content Security Policy
3. Application error disclosure (stack traces in 500 responses)
4. FTP directory listing exposes sensitive files
5. Backup files accessible (.bak)
6. Timestamps in CSS (Unix epoch disclosure)
7. JWT authentication via Authorization header
8. SPA architecture with hash-based routing