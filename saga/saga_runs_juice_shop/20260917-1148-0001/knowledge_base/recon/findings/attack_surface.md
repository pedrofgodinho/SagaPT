# OWASP Juice Shop - Attack Surface

## Application Overview
- **Application:** OWASP Juice Shop v14+ (deliberately vulnerable web app)
- **Tech Stack:** Node.js, Express ^4.22.1, Angular SPA (client-side routing via `#` hash fragments)
- **Frontend:** Angular with Material Design components
- **Backend:** Express REST API
- **Database:** SQLite (implied by Sequelize ORM in stacktrace)
- **Hosting:** Local instance at `http://juiceshop.local:3000`

## Discovered Endpoints

### Authentication Endpoints
| Method | Endpoint | Inputs | Status |
|--------|----------|--------|--------|
| POST | `/rest/user/login` | `email`, `password` (JSON body) | ✅ Working - returns JWT token |
| POST | `/api/Users` | `email`, `password`, `securityQuestion.id`, `securityAnswer` (JSON body) | ✅ Working - user registration (201 Created) |
| GET | `/api/Users` | None (requires auth) | 🔒 Requires auth (401 without) |

### Product/Commerce Endpoints
| Method | Endpoint | Inputs | Status |
|--------|----------|--------|--------|
| GET | `/api/Products` | None | ✅ Working - returns JSON array of products (36 items) |
| GET | `/api/Order` | None | ❌ Not found (500) |
| GET | `/api/Basket` | None | ❌ Not found (500) |
| GET | `/api/Coupons` | None | ❌ Not found (500) |
| GET | `/api/Complaint` | None | ❌ Not found (500) |

### User/Security Endpoints
| Method | Endpoint | Inputs | Status |
|--------|----------|--------|--------|
| GET | `/api/SecurityQuestions` | None | ✅ Working - returns 14 security questions |
| GET | `/api/Me` | None | ❌ Not found (500) |
| GET | `/api/Users` | None | 🔒 Requires auth |

### Angular SPA Hash Routes (client-side)
| Route | Description |
|-------|-------------|
| `/#/` | Home page |
| `/#/login` | Login page |
| `/#/register` | Registration page |
| `/#/jobs` | Jobs/careers page (linked from `X-Recruiting` header) |
| `/#/recycle` | Recycling page |

### Static Assets
| Path | Type |
|------|------|
| `/styles.css` | Stylesheet |
| `/scripts.js` | Cookie consent script |
| `/main.js` | Angular main bundle (~1.2MB) |
| `/polyfills.js` | Angular polyfills |
| `/assets/public/favicon_js.ico` | Favicon |
| `/assets/public/images/uploads/default.svg` | Default profile image |

### FTP Directory (publicly accessible, robots.txt disallows but not enforced)
| Path | Description |
|------|-------------|
| `/ftp/` | Directory listing |
| `/ftp/acquisitions.md` | Confidential acquisition plans |
| `/ftp/announcement_encrypted.md` | Encrypted announcement (369KB) |
| `/ftp/coupons_2013.md.bak` | Backup file (403 - only .md/.pdf allowed) |
| `/ftp/eastere.gg` | Easter egg file |
| `/ftp/encrypt.pyc` | Python bytecode file |
| `/ftp/incident-support.kdbx` | KeePass database file (3.2KB) |
| `/ftp/legal.md` | Legal document |
| `/ftp/package.json.bak` | Package backup |
| `/ftp/package-lock.json.bak` | Lock file backup |
| `/ftp/quarantine/` | Directory with quarantine files |
| `/ftp/quarantine/juicy_malware_macos_64.url` | Malware URL |
| `/ftp/quarantine/juicy_malware_linux_amd_64.url` | Malware URL |
| `/ftp/quarantine/juicy_malware_linux_arm_64.url` | Malware URL |
| `/ftp/quarantine/juicy_malware_windows_64.exe.url` | Malware URL |

### Other Discovered Paths
| Path | Description |
|------|-------------|
| `/robots.txt` | Disallows `/ftp` |
| `/sitemap.xml` | Returns Angular shell (SPA) |
| `/api/v1/users` | ❌ Not found (500) |
| `/api/v2/products` | ❌ Not found (500) |
| `/api/Categories` | ❌ Not found (500) |
| `/api/Feedback` | ❌ Not found (500) |

## Input Parameters Summary

### Form/JSON Inputs
- **Registration:** `email`, `password`, `securityQuestion.id`, `securityAnswer`
- **Login:** `email`, `password`
- **Products API:** None (GET)

### Query String Parameters
- None discovered directly (SPA uses hash routing)

### HTTP Headers
- `Authorization: Bearer <JWT>` - Required for authenticated endpoints
- `Content-Type: application/json` - For API requests

### URL Parameters
- None (SPA uses hash-based routing)

## Security Observations

### Headers
- `Access-Control-Allow-Origin: *` - **CORS misconfiguration** (all origins allowed)
- `X-Content-Type-Options: nosniff` - Present
- `X-Frame-Options: SAMEORIGIN` - Present
- `Feature-Policy: payment 'self'` - Present
- `X-Recruiting: /#/jobs` - Custom header pointing to jobs page
- **Missing:** Content Security Policy (CSP) header

### Sensitive Data Exposure
- FTP directory accessible despite robots.txt
- `incident-support.kdbx` (KeePass database) publicly downloadable
- `acquisitions.md` contains confidential business information
- `package.json.bak` and `package-lock.json.bak` expose dependency info
- Timestamps disclosed in CSS files (Unix epoch)
- Stack traces visible on 500 errors (application error disclosure)

### Authentication
- JWT-based authentication (RS256 signing)
- Token returned in `authentication.token` field
- Session ID (`bid`) and user email (`umail`) also in response

### Known Credentials (from registration)
- Email: `recon@test.com`
- Password: `TestPass123!`
- User ID: 25
- Role: customer

## ZAP Alerts Detected
1. **Cross-Domain Misconfiguration** (Medium) - `Access-Control-Allow-Origin: *`
2. **Content Security Policy Not Set** (Medium) - No CSP header
3. **Application Error Disclosure** (Low) - Stack traces on 500 errors
4. **Timestamp Disclosure** (Low) - Unix timestamps in CSS
5. **Authentication Request Identified** (Info) - Login endpoints
6. **Session Management Response Identified** (Info) - JWT token in response