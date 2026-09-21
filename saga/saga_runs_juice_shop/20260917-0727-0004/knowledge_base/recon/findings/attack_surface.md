# Attack Surface - OWASP Juice Shop (http://juiceshop.local:3000)

## Technology Stack
- **Backend:** Node.js with Express ^4.22.1
- **Frontend:** Angular SPA (Material design components)
- **Database:** SQLite (Juice Shop default)
- **Language:** JavaScript/TypeScript
- **Authentication:** JWT-based (Authorization header)
- **CORS:** `Access-Control-Allow-Origin: *` (open to all origins)

## Test Account
- **Email:** recon@test.com
- **Password:** ReconPass123!
- **User ID:** 25
- **Registration endpoint:** `POST /api/Users/`
- **Login endpoint:** `POST /api/authenticate/login`

---

## Discovered Endpoints

### Static / SPA Routes
| Method | Endpoint | Auth Required | Notes |
|--------|----------|--------------|-------|
| GET | `/` | No | Homepage (Angular SPA shell) |
| GET | `/#/register` | No | Registration page (SPA) |
| GET | `/#/jobs` | No | Jobs page (referenced via X-Recruiting header) |
| GET | `/main.js` | No | Angular main bundle |
| GET | `/polyfills.js` | No | Angular polyfills |
| GET | `/scripts.js` | No | App scripts |
| GET | `/styles.css` | No | App styles |
| GET | `/assets/public/favicon_js.ico` | No | Favicon |

### Public API Endpoints
| Method | Endpoint | Auth Required | Input Parameters |
|--------|----------|--------------|------------------|
| GET | `/api/Products` | No | Query: `limit` (tested) |
| GET | `/api/Products/{id}` | No | Path: `id` (integer) |
| GET | `/api/SecurityQuestions` | No | None |
| GET | `/api/SecurityQuestions/{id}` | Yes | Path: `id` (integer) |
| POST | `/api/authenticate/login` | No | Body: `email`, `password` |
| POST | `/api/Users/` | No | Body: `email`, `password`, `securityQuestion.id`, `securityQuestion.answer`, `name` |

### Authenticated API Endpoints
| Method | Endpoint | Auth Required | Notes |
|--------|----------|--------------|-------|
| GET | `/api/Users` | Yes | User listing |
| GET | `/api/Users/{id}` | Yes | Path: `id` (integer) |
| GET | `/api/PrivacyRequests` | Yes | Privacy request management |
| GET | `/api/Complaints` | Yes | Complaints endpoint |
| GET | `/api/Orders` | Yes | Returns 500 - path not found (not a valid endpoint) |
| GET | `/api/Restaurants` | Yes | Returns 500 - path not found (not a valid endpoint) |
| GET | `/api/Transactions` | Yes | Returns 500 - path not found (not a valid endpoint) |
| GET | `/api/Address/` | Yes | Returns 500 - path not found (not a valid endpoint) |
| GET | `/api/Countries` | Yes | Returns 500 - path not found (not a valid endpoint) |
| GET | `/api/Feedback` | Yes | Returns 500 - path not found (not a valid endpoint) |
| GET | `/api/Coupons` | Yes | Returns 500 - path not found (not a valid endpoint) |

### FTP / File Server Endpoints
| Method | Endpoint | Auth Required | Notes |
|--------|----------|--------------|-------|
| GET | `/ftp/` | No | Directory listing |
| GET | `/ftp/acquisitions.md` | No | Confidential document (planned acquisitions) |
| GET | `/ftp/announcement_encrypted.md` | No | Encrypted announcement (369KB) |
| GET | `/ftp/coupons_2013.md.bak` | No | Backup file |
| GET | `/ftp/eastere.gg` | No | Game file |
| GET | `/ftp/encrypt.pyc` | No | Python bytecode file |
| GET | `/ftp/incident-support.kdbx` | No | KeePass password database |
| GET | `/ftp/legal.md` | No | Legal document |
| GET | `/ftp/package.json.bak` | No | Backup file |
| GET | `/ftp/package-lock.json.bak` | No | Backup file |
| GET | `/ftp/quarantine/` | No | Quarantine directory |
| GET | `/ftp/quarantine/juicy_malware_macos_64.url` | No | Malware URL shortcut |
| GET | `/ftp/quarantine/juicy_malware_linux_amd_64.url` | No | Malware URL shortcut |
| GET | `/ftp/quarantine/juicy_malware_linux_arm_64.url` | No | Malware URL shortcut |
| GET | `/ftp/quarantine/juicy_malware_windows_64.exe.url` | No | Malware URL shortcut |

### Informational Endpoints
| Method | Endpoint | Auth Required | Notes |
|--------|----------|--------------|-------|
| GET | `/robots.txt` | No | Disallows `/ftp` |
| GET | `/sitemap.xml` | No | Returns SPA shell (not a real sitemap) |

---

## Input Points Checklist

### Query Parameters
- [x] `limit` on `GET /api/Products` (pagination/limit parameter)

### Path Parameters
- [x] `id` on `GET /api/Products/{id}` (integer, product ID)
- [x] `id` on `GET /api/SecurityQuestions/{id}` (integer, question ID)
- [x] `id` on `GET /api/Users/{id}` (integer, user ID)
- [x] `{filename}` on `GET /ftp/{filename}` (file path traversal)

### POST Body Fields
- [x] `email`, `password` on `POST /api/authenticate/login` (authentication)
- [x] `email`, `password`, `securityQuestion.id`, `securityQuestion.answer`, `name` on `POST /api/Users/` (registration)

### Headers
- [x] `Authorization` (JWT token for authenticated endpoints)
- [x] `Content-Type` (application/json for API endpoints)

### Security Headers Present
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Feature-Policy: payment 'self'`
- `X-Recruiting: /#/jobs` (information disclosure)

### Security Headers Missing
- Content Security Policy (CSP)
- Strict-Transport-Security
- X-XSS-Protection

---

## Key Discoveries
1. **Open CORS:** `Access-Control-Allow-Origin: *` on all endpoints
2. **Unauthenticated user registration:** `POST /api/Users/` allows creating accounts without any validation
3. **Sensitive files in /ftp/:** Including KeePass database, backup files, encrypted documents, and confidential acquisition plans
4. **Stack trace disclosure:** 500 errors reveal full Express stack traces with file paths
5. **Angular SPA:** All routes return the same shell; navigation is client-side via `/#/` hash routing
6. **X-Recruiting header:** Points to `/#/jobs` page
7. **File type restriction on /ftp/:** Only `.md` and `.pdf` files allowed (403 on other types)
8. **Security questions publicly accessible:** All 14 security questions retrievable without auth
9. **Products API fully public:** All product data accessible without authentication
10. **Multiple dead API paths:** `/api/Orders`, `/api/Countries`, `/api/Feedback`, `/api/Coupons`, `/api/Restaurants`, `/api/Transactions`, `/api/Address/` all return 500 errors (not implemented)
