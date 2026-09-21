# OWASP Juice Shop - Attack Surface Reconnaissance

## Target
**URL:** http://juiceshop.local:3000
**Application:** OWASP Juice Shop (v16.x, built for security research)

---

## Technology Stack

| Component | Details |
|-----------|---------|
| **Backend Framework** | Express.js ^4.22.1 (Node.js) |
| **Frontend Framework** | Angular SPA (hash-based routing `/#/...`) |
| **API Format** | JSON REST API |
| **Authentication** | Form-based (JWT/Bearer token) |
| **Database** | SQLite (implied by Juice Shop default) |
| **Static Assets** | Angular build output (main.js, scripts.js, polyfills.js, styles.css) |
| **Font** | VT323 (Google Fonts), Roboto (Material) |

---

## Security Headers Observed

- `Access-Control-Allow-Origin: *` (CORS wildcard - cross-domain misconfiguration)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Feature-Policy: payment 'self'`
- `X-Recruiting: /#/jobs`
- **Missing:** Content-Security-Policy (CSP) header NOT set
- **Missing:** Strict-Transport-Security (HSTS)
- **Missing:** X-XSS-Protection

---

## Discovered Endpoints

### Static & Public Pages (GET)
| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/` | GET | 200 | Main SPA shell (Angular) |
| `/styles.css` | GET | 200 | Stylesheet (contains timestamp disclosure) |
| `/scripts.js` | GET | 200 | Client-side scripts |
| `/main.js` | GET | 200 | Angular main bundle |
| `/polyfills.js` | GET | 200 | Angular polyfills |
| `/favicon_js.ico` | GET | 200 | Favicon |
| `/assets/public/favicon_js.ico` | GET | 200 | Favicon (alternate path) |
| `/robots.txt` | GET | 200 | Disallows `/ftp` |
| `/sitemap.xml` | GET | 200 | Sitemap (returns SPA HTML) |
| `/ftp/` | GET | 200 | FTP directory listing (exposed!) |
| `/ftp/acquisitions.md` | GET | 200 | Acquisitions document |
| `/ftp/announcement_encrypted.md` | GET | 200 | Encrypted announcement |
| `/ftp/coupons_2013.md.bak` | GET | 200 | Backup file (sensitive!) |
| `/ftp/eastere.gg` | GET | 200 | Easter egg file |
| `/ftp/encrypt.pyc` | GET | 200 | Python bytecode file |
| `/ftp/incident-support.kdbx` | GET | 200 | KeePass database (sensitive!) |
| `/ftp/legal.md` | GET | 200 | Legal document |
| `/ftp/package-lock.json.bak` | GET | 200 | Backup file |
| `/ftp/package.json.bak` | GET | 200 | Backup file |
| `/ftp/quarantine/` | GET | 200 | Quarantine directory |
| `/ftp/quarantine/juicy_malware_linux_arm_64.url` | GET | 200 | Malware URL file |
| `/ftp/quarantine/juicy_malware_linux_amd_64.url` | GET | 200 | Malware URL file |
| `/ftp/quarantine/juicy_malware_macos_64.url` | GET | 200 | Malware URL file |
| `/ftp/quarantine/juicy_malware_windows_64.exe.url` | GET | 200 | Malware URL file |
| `/ftp/suspicious_errors.yml` | GET | 200 | Error log file |

### API Endpoints (REST)
| Endpoint | Method | Status | Description | Input Parameters |
|----------|--------|--------|-------------|------------------|
| `/api/products` | GET | 200 | Product catalog (public) | None |
| `/api/users` | GET | 401 | User listing (auth required) | None |
| `/api/v1/user` | GET | 500 | User endpoint (not found) | None |
| `/api/v1/users` | GET | 500 | Users endpoint (not found) | None |
| `/api/v1/products` | GET | 500 | Products endpoint (not found) | None |
| `/api/v1/orders` | GET | 500 | Orders endpoint (not found) | None |
| `/api/v1/addresses` | GET | 500 | Addresses endpoint (not found) | None |
| `/api/v1/security` | GET | 500 | Security endpoint (not found) | None |
| `/api/v1/captcha` | GET | 500 | Captcha endpoint (not found) | None |
| `/api/v1/privacy-requests` | GET | 500 | Privacy requests (not found) | None |
| `/api/v1/redirect` | GET | 500 | Redirect endpoint (not found) | None |
| `/api/v1/payment-methods` | GET | 500 | Payment methods (not found) | None |
| `/api/v1/feedback` | GET | 500 | Feedback endpoint (not found) | None |
| `/api/user` | POST | 500 | User registration attempt | `email`, `password` |
| `/api/user/` | POST | 500 | User registration attempt | `email`, `password` |
| `/api/auth/login` | POST | 500 | Login attempt | `email`, `password` |
| `/api/v1/user/anonymous/` | POST | 500 | Anonymous user endpoint | `email`, `password` |
| `/rest/user` | POST | 500 | REST user endpoint | `email`, `password` |
| `/rest/user/register` | POST | 500 | REST registration | `email`, `password` |

### SPA Routes (Angular, GET)
| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/#/` | GET | 200 | Home page |
| `/#/signup` | GET | 200 | Registration page |
| `/#/login` | GET | 200 | Login page |
| `/#/jobs` | GET | 200 | Jobs page (per X-Recruiting header) |

---

## Input Points Summary

### Form Fields (SPA-rendered, client-side)
- **Registration form** (`/#/signup`): `email`, `password`, `securityQuestion` (id + answer), `securityAnswer`
- **Login form** (`/#/login`): `email`, `password`

### API Request Bodies (POST)
- User registration: `email` (string), `password` (string)
- Login: `email` (string), `password` (string)

### Query Parameters
- None discovered in static endpoints
- Product API may support filtering (not tested)

### File Upload Points
- None discovered (no upload endpoints found)

---

## Notable Findings

1. **FTP Directory Exposed**: `/ftp/` is publicly accessible and contains:
   - KeePass database (`incident-support.kdbx`) - potentially contains credentials
   - Backup files (`.bak`) - may contain sensitive data
   - Encrypted announcement
   - Quarantine files (malware samples)
   - Error logs (`suspicious_errors.yml`)

2. **CORS Misconfiguration**: `Access-Control-Allow-Origin: *` on all endpoints

3. **Missing CSP**: No Content-Security-Policy header

4. **Timestamp Disclosure**: Unix timestamps found in CSS files

5. **Application Error Disclosure**: Stack traces returned on 500 errors (Express.js debug mode)

6. **Angular SPA**: All page content is client-side rendered; forms are not visible in raw HTML

---

## Test Account Credentials

**Registration attempt:** `recon@test.com` / `ReconPass123`
- Registration endpoint was not successfully identified (all attempts returned 500)
- The registration form exists at `/#/signup` (Angular SPA)
- Expected form fields: `email`, `password`, `securityQuestion` (id + answer)
- **Note:** The actual API endpoint for registration was not determinable through HTTP probing alone - it is likely handled by Angular client-side logic calling a different API path

---

## Summary Statistics

- **Total URLs discovered:** 66 (via spider)
- **Working API endpoints:** 1 (`/api/products` GET)
- **Protected endpoints:** 1 (`/api/users` GET - requires auth)
- **SPA routes:** 3+ (signup, login, jobs)
- **FTP files:** 15+ files including sensitive backups and databases
- **ZAP alerts raised:** 15 (CORS, timestamp disclosure, missing CSP, auth request identification)