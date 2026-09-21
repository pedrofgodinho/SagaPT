# OWASP Juice Shop - Attack Surface Map

## Application Overview
- **Application**: OWASP Juice Shop (v14+)
- **Backend**: Express.js ^4.22.1 (Node.js)
- **Frontend**: Angular SPA (hash-based routing)
- **Host**: http://juiceshop.local:3000
- **Copyright**: Bjoern Kimminich & the OWASP Juice Shop contributors

## Technology Stack
- **Web Server**: Express.js (Node.js)
- **Frontend Framework**: Angular (Material Design components)
- **Styling**: CSS with CSS custom properties (Material Design theming)
- **Font**: VT323 (Google Fonts), Roboto (Material)
- **Authentication**: Form-based (HTTP POST)
- **API Style**: REST API + GraphQL (potential)

## Security Headers Observed
- `Access-Control-Allow-Origin: *` (CORS wildcard - **Medium Risk**)
- `X-Content-Type-Options: nosniff` (Present)
- `X-Frame-Options: SAMEORIGIN` (Present)
- `Feature-Policy: payment 'self'` (Present)
- `X-Recruiting: /#/jobs` (Information disclosure)
- **Missing**: Content-Security-Policy (CSP), X-XSS-Protection

---

## Discovered Endpoints & Input Points

### 1. Authentication Endpoints
| Endpoint | Method | Input Parameters | Status |
|----------|--------|-----------------|--------|
| `/rest/user/login` | POST | `email`, `password` | **WORKS** - Returns 401 for invalid creds, 26-byte error message |
| `/rest/user/login` | GET | - | Returns 500 (Angular catches) |
| `/#/login` | GET | - | Angular SPA route (hash routing) |
| `/#/register` | GET | - | Angular SPA route (hash routing) |

**Registration**: `/rest/user/signup` POST returns 500 error consistently (Angular catches). Form-based and JSON content types both fail. Registration may need to be done through the Angular SPA frontend.

### 2. User Management Endpoints
| Endpoint | Method | Input Parameters | Status |
|----------|--------|-----------------|--------|
| `/rest/user/me` | GET | - | Returns 500 (Angular catches) |
| `/rest/user/signup` | POST | `name`, `email`, `password`, `securityQuestion.id`, `securityQuestion.answer`, `creditCard.number`, `creditCard.expirationDate`, `creditCard.cardCode` | Returns 500 |

### 3. Product/Store Endpoints
| Endpoint | Method | Input Parameters | Status |
|----------|--------|-----------------|--------|
| `/rest/products` | GET | - | Returns 500 (Angular catches) |
| `/rest/order` | GET | - | Returns 500 (Angular catches) |
| `/rest/coupon` | GET | - | Returns 500 (Angular catches) |
| `/rest/payment-method` | GET | - | Returns 500 (Angular catches) |
| `/rest/recycle` | GET | - | Returns 500 (Angular catches) |
| `/rest/feedback` | GET | - | Returns 500 (Angular catches) |
| `/rest/securityQuestion` | GET | - | Returns 500 (Angular catches) |

### 4. API/GraphQL Endpoints
| Endpoint | Method | Input Parameters | Status |
|----------|--------|-----------------|--------|
| `/graphql` | POST | `query` (GraphQL query) | Returns Angular SPA shell (may be non-functional or needs different content-type) |
| `/api` | GET | - | Returns 500 |
| `/api/v1/users` | GET | - | Returns 500 |
| `/api/v1/products` | GET | - | Returns 500 |

### 5. Admin/Management Endpoints
| Endpoint | Method | Input Parameters | Status |
|----------|--------|-----------------|--------|
| `/admin` | GET | - | Returns Angular SPA shell |
| `/#/admin` | GET | - | Angular SPA route |
| `/#/jobs` | GET | - | Referenced in X-Recruiting header |

### 6. Static File Endpoints (FTP Directory)
| Endpoint | Method | Input Parameters | Status |
|----------|--------|-----------------|--------|
| `/ftp/` | GET | - | **200** - Directory listing |
| `/ftp/acquisitions.md` | GET | - | **200** - Confidential acquisition plans (markdown) |
| `/ftp/legal.md` | GET | - | **200** - Legal information + Terms of Use (markdown) |
| `/ftp/announcement_encrypted.md` | GET | - | **200** - Encrypted announcement (369KB, large numeric data) |
| `/ftp/incident-support.kdbx` | GET | - | **200** - KeePass database file (3246 bytes, binary) |
| `/ftp/quarantine/` | GET | - | Directory listing |
| `/ftp/quarantine/juicy_malware_macos_64.url` | GET | - | **200** - Internet shortcut to malicious macOS binary |
| `/ftp/quarantine/juicy_malware_linux_amd_64.url` | GET | - | **200** - Internet shortcut to malicious Linux binary |
| `/ftp/quarantine/juicy_malware_linux_arm_64.url` | GET | - | **200** - Internet shortcut to malicious Linux ARM binary |
| `/ftp/quarantine/juicy_malware_windows_64.exe.url` | GET | - | **200** - Internet shortcut to malicious Windows executable |

### 7. Blocked FTP Files (403 - Only .md and .pdf allowed)
| Endpoint | Method | Status |
|----------|--------|--------|
| `/ftp/package.json.bak` | GET | 403 |
| `/ftp/package-lock.json.bak` | GET | 403 |
| `/ftp/suspicious_errors.yml` | GET | 403 |
| `/ftp/coupons_2013.md.bak` | GET | 403 |
| `/ftp/eastere.gg` | GET | 403 |
| `/ftp/encrypt.pyc` | GET | 403 |

### 8. Robots & Sitemap
| Endpoint | Method | Input Parameters | Status |
|----------|--------|-----------------|--------|
| `/robots.txt` | GET | - | **200** - `User-agent: *\nDisallow: /ftp` |
| `/sitemap.xml` | GET | - | **200** - Returns Angular SPA shell |

### 9. Documentation Endpoints
| Endpoint | Method | Input Parameters | Status |
|----------|--------|-----------------|--------|
| `/docs` | GET | - | Returns Angular SPA shell |
| `/swagger` | GET | - | Returns Angular SPA shell |

### 10. Static Assets
| Endpoint | Method | Status |
|----------|--------|--------|
| `/styles.css` | GET | 200 - Contains Unix timestamps (disclosure) |
| `/scripts.js` | GET | 200 |
| `/polyfills.js` | GET | 200 |
| `/main.js` | GET | 200 |
| `/assets/public/favicon_js.ico` | GET | 200 |

---

## Input Points Summary

### Form Fields (Login)
- `email` (text input)
- `password` (password input)

### Form Fields (Registration - expected)
- `name` (text input)
- `email` (text input)
- `password` (password input)
- `securityQuestion.id` (numeric dropdown)
- `securityQuestion.answer` (text input)
- `creditCard.number` (text input)
- `creditCard.expirationDate` (text input)
- `creditCard.cardCode` (text input)

### URL Parameters (potential)
- Hash fragment routing: `/#/login`, `/#/register`, `/#/admin`, `/#/jobs`

### API Request Bodies
- Login: JSON `{email, password}` or form-urlencoded
- Registration: JSON with user data, security question, credit card

### File Upload/Download
- `/ftp/` directory allows reading `.md` and `.pdf` files only
- Binary files (.kdbx, .url, .pyc, .gg) return 403 except `.kdbx` which returned 200 binary data
- Quarantine directory contains malware shortcut files

---

## Security Observations

1. **CORS Wildcard** (`Access-Control-Allow-Origin: *`) - All endpoints expose this
2. **No CSP** - Content-Security-Policy header missing
3. **Application Error Disclosure** - Stack traces visible on 500 errors (Express paths disclosed)
4. **Timestamp Disclosure** - Unix timestamps in CSS files
5. **Sensitive Files Exposed** - FTP directory contains:
   - Encrypted announcement with large numeric data
   - KeePass database file (incident-support.kdbx)
   - Malware quarantine shortcuts
   - Confidential acquisition plans
6. **File Type Validation Bypass** - FTP server restricts to .md/.pdf but .kdbx was served
7. **Angular SPA** - All pages return same HTML shell; client-side routing handles navigation
8. **Hash-based Routing** - All Angular routes use `/#/` prefix

## Known Credentials (from Juice Shop defaults)
- Admin: `admin@juiceshop.local` / `admin`
- User: `bender@juiceshop.local` / `KriegerSucks`
- Various other test accounts exist in the application
