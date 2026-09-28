# OWASP Juice Shop - Attack Surface Inventory

## Application Overview
- **Application:** OWASP Juice Shop (v16.x)
- **Framework:** Express.js ^4.22.1 (Node.js)
- **Frontend:** Angular SPA (Material Design)
- **Target:** http://juiceshop.local:3000

## Technology Stack
- **Backend:** Node.js, Express.js 4.22.1
- **Frontend:** Angular with Angular Material (MatDialog, MatCheckbox, etc.)
- **Database:** SQLite (inferred from Juice Shop defaults)
- **Authentication:** JWT-based (Bearer token in Authorization header)
- **CORS:** `Access-Control-Allow-Origin: *` (open to all origins)
- **Other Headers:** X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Feature-Policy: payment 'self', X-Recruiting: /#/jobs

## Discovered Endpoints

### Public REST API Endpoints
| Endpoint | Method | Auth Required | Notes |
|----------|--------|---------------|-------|
| `/api/Products` | GET | No | Returns full product catalog (20+ items) |
| `/api/SecurityQuestions` | GET | No | Returns 14 security questions (id, question text) |
| `/rest/user/whoami` | GET | No | Returns `{"user":{}}` when unauthenticated |
| `/rest/web3/nftUnlocked` | GET | No | Web3/NFT related endpoint |
| `/rest/web3/nftMintListen` | GET | No | NFT minting status |
| `/rest/web3/submitKey` | POST | No | Private key submission |
| `/rest/web3/walletNFTVerify` | POST | No | Wallet address verification |
| `/rest/web3/walletExploitAddress` | POST | No | Wallet exploit endpoint |

### Authenticated REST API Endpoints
| Endpoint | Method | Auth Required | Notes |
|----------|--------|---------------|-------|
| `/api/Users` | GET | Yes (401 without) | User data |
| `/api/PrivacyRequests` | GET | Yes (401 without) | Privacy data requests |
| `/api/Order` | GET | Yes (expected) | Order history |
| `/api/Cart` | GET | Yes (expected) | Shopping cart |
| `/api/Feedback` | GET/POST | Yes (expected) | User feedback |
| `/api/Complaint` | GET/POST | Yes (expected) | Complaints |
| `/api/Recycle` | GET/POST | Yes (expected) | Recycling program |
| `/api/Challenge` | GET | Yes (expected) | CTF challenges |

### Authentication Endpoints
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|------------------|-------|
| `/rest/user/login` | POST | `email`, `password` | Form-based login. Returns "Invalid email or password." on failure. JWT token on success. |
| `/rest/user/signup` | POST | `email`, `password`, `securityQuestionId`, `securityAnswer` | Registration via SPA. Returns 500 when accessed directly. |
| `/api/auth/login` | POST | `email`, `password` | Identified by ZAP as auth endpoint but returns 500 |
| `/api/auth/signup` | POST | `email`, `password`, `securityQuestionId`, `securityAnswer` | Returns 500 - not a direct REST endpoint |

### Admin & SPA Routes
| Endpoint | Method | Notes |
|----------|--------|-------|
| `/#/admin` | GET | Admin panel (SPA route) |
| `/#/login` | GET | Login page (SPA route) |
| `/#/signup` | GET | Registration page (SPA route) |
| `/#/jobs` | GET | Jobs page (referenced in X-Recruiting header) |
| `/#/recycle` | GET | Recycling page |
| `/#/contact` | GET | Contact page |
| `/#/privacy-security` | GET | Privacy & security page |

### FTP File Server (Restricted to .md and .pdf)
| Endpoint | Method | Notes |
|----------|--------|-------|
| `/ftp/` | GET | Directory listing |
| `/ftp/acquisitions.md` | GET | Confidential - planned acquisitions (909 bytes) |
| `/ftp/legal.md` | GET | Legal information (3047 bytes) |
| `/ftp/announcement_encrypted.md` | GET | Large encrypted announcement (369KB, contains numeric data) |
| `/ftp/coupons_2013.md.bak` | GET | Returns 403 - .bak extension blocked |
| `/ftp/encrypt.pyc` | GET | Returns 403 - .pyc extension blocked |
| `/ftp/eastere.gg` | GET | Returns 403 - .gg extension blocked |
| `/ftp/suspicious_errors.yml` | GET | Returns 403 - .yml extension blocked |
| `/ftp/package.json.bak` | GET | Returns 403 - .bak extension blocked |
| `/ftp/quarantine/` | GET | Directory listing with malware URL files |
| `/ftp/quarantine/juicy_malware_linux_amd_64.url` | GET | Malware URL file |
| `/ftp/quarantine/juicy_malware_linux_arm_64.url` | GET | Malware URL file |
| `/ftp/quarantine/juicy_malware_macos_64.url` | GET | Malware URL file |
| `/ftp/quarantine/juicy_malware_windows_64.exe.url` | GET | Malware URL file |

### Static Assets
| Endpoint | Method | Notes |
|----------|--------|-------|
| `/main.js` | GET | Angular bundle (1.2MB) |
| `/scripts.js` | GET | Cookie consent script |
| `/polyfills.js` | GET | Zone.js polyfills |
| `/styles.css` | GET | Application styles |
| `/robots.txt` | GET | Disallows `/ftp` |
| `/sitemap.xml` | GET | Returns SPA HTML (SPA-based sitemap) |
| `/assets/public/favicon_js.ico` | GET | Favicon |

### Common Paths (Not Found / SPA Routes)
| Endpoint | Method | Notes |
|----------|--------|-------|
| `/admin` | GET | Returns SPA HTML (200) |
| `/api/v1` | GET | Returns 500 - "Unexpected path" |
| `/docs` | GET | Returns SPA HTML (200) |
| `/swagger` | GET | Returns SPA HTML (200) |
| `/api/Product` | GET | Returns 500 - "Unexpected path" |
| `/api/Country` | GET | Returns 500 - "Unexpected path" |
| `/api/Contact` | GET | Returns 500 - "Unexpected path" |
| `/api/Feedback` | GET | Returns 500 - "Unexpected path" |
| `/api/Complaint` | GET | Returns 500 - "Unexpected path" |
| `/api/Recycle` | GET | Returns 500 - "Unexpected path" |
| `/api/Challenge` | GET | Returns 500 - "Unexpected path" |
| `/api/SecurityQuestion` | POST | Returns 500 - "Unexpected path" |

## Input Points

### Form Fields
- **Login form:** `email` (text), `password` (password)
- **Registration form:** `email` (text), `password` (password), `securityQuestionId` (integer 1-14), `securityAnswer` (text)
- **Cookie consent:** `cc-btn` (allow, deny, dismiss)

### Query Parameters
- Products API supports query parameters (filtering, pagination)
- Security Questions API supports query parameters

### HTTP Headers
- `Authorization: Bearer <token>` - JWT authentication
- `Content-Type` - application/json or application/x-www-form-urlencoded

### URL Parameters
- Product IDs in URLs (e.g., `/api/Products/1`)
- User IDs in URLs (e.g., `/api/Users/1`)
- Security question IDs (1-14)

### File Upload
- FTP file server accepts .md and .pdf files only
- File type validation may be bypassable via extension manipulation

## Security Observations
1. **CORS wide open:** `Access-Control-Allow-Origin: *` on all responses
2. **No CSP header:** Content Security Policy not set
3. **Application error disclosure:** 500 errors reveal Express stack traces with file paths (`/juice-shop/build/routes/...`)
4. **Timestamp disclosure:** Unix timestamps in CSS files
5. **Sensitive files exposed:** FTP directory contains confidential acquisition plans
6. **JWT authentication:** Bearer token based, token obtained via `/rest/user/login`
7. **SPA architecture:** All routes serve same HTML shell, routing handled client-side
8. **Default credentials likely present:** OWASP Juice Shop ships with default admin account
9. **Web3/NFT endpoints:** Additional attack surface for crypto-related vulnerabilities
10. **File type restriction:** FTP server only allows .md and .pdf - potential bypass opportunity

## Known Default Credentials (to be verified)
- Admin: `admin@juice-shop.io` / `juiceshop`
- User: `bender@juice-shop.io` / `Kronos123`
- User: `demotiv8@juice-shop.io` / `8uiGh!@#$`