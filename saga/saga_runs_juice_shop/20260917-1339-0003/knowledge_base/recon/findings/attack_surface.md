# OWASP Juice Shop - Complete Attack Surface

## Application Overview
- **Target**: http://juiceshop.local:3000
- **Application**: OWASP Juice Shop v17+ (deliberately vulnerable web app)
- **Framework**: Express.js ^4.22.1 (Node.js)
- **Frontend**: Angular SPA (client-side routing with `/#/` hash routes)
- **Tech Stack**: Node.js, Express, Angular, Material Design

## Discovered Endpoints

### Static Assets & Public Pages
| Path | Method | Description |
|------|--------|-------------|
| `/` | GET | Main application shell (Angular SPA) |
| `/styles.css` | GET | Application styles |
| `/scripts.js` | GET | Application scripts |
| `/polyfills.js` | GET | Browser polyfills |
| `/main.js` | GET | Angular main bundle (~1.2MB) |
| `/assets/public/favicon_js.ico` | GET | Favicon |
| `/robots.txt` | GET | Disallows `/ftp` |
| `/sitemap.xml` | GET | Sitemap (returns HTML shell) |
| `/swagger.json` | GET | Swagger endpoint (returns HTML shell) |

### FTP File Server
| Path | Method | Description |
|------|--------|-------------|
| `/ftp/` | GET | Directory listing |
| `/ftp/acquisitions.md` | GET | Confidential acquisitions doc |
| `/ftp/legal.md` | GET | Legal information |
| `/ftp/announcement_encrypted.md` | GET | Encrypted announcement (369KB, contains large numeric strings) |
| `/ftp/coupons_2013.md.bak` | GET | Backup file (403 - only .md/.pdf allowed) |
| `/ftp/eastere.gg` | GET | Easter egg file (403 - only .md/.pdf allowed) |
| `/ftp/encrypt.pyc` | GET | Python compiled file (403 - only .md/.pdf allowed) |
| `/ftp/incident-support.kdbx` | GET | KeePass database (3.2KB) |
| `/ftp/quarantine/` | GET | Directory listing with malware shortcuts |
| `/ftp/quarantine/juicy_malware_linux_amd_64.url` | GET | Malware URL shortcut (Linux) |
| `/ftp/quarantine/juicy_malware_linux_arm_64.url` | GET | Malware URL shortcut (Linux ARM) |
| `/ftp/quarantine/juicy_malware_macos_64.url` | GET | Malware URL shortcut (macOS) |
| `/ftp/quarantine/juicy_malware_windows_64.exe.url` | GET | Malware URL shortcut (Windows) |

### API Endpoints
| Path | Method | Description |
|------|--------|-------------|
| `/rest/user/login` | POST | User authentication (JSON body) |
| `/rest/user/registration` | POST | User registration (500 - not accessible) |
| `/rest/user/register` | POST | User registration alt (500 - not accessible) |
| `/api/v1/user/login` | POST | User login (500 - intercepted by Angular) |
| `/api/v1/user/registration` | POST | User registration (500 - intercepted by Angular) |
| `/api/v1/users` | GET | Users list (500 - intercepted by Angular) |
| `/api/v1/user` | GET | User endpoint (500 - intercepted by Angular) |
| `/api/v1/products` | GET | Products (500 - intercepted by Angular) |

### Angular Hash Routes (SPA)
| Path | Method | Description |
|------|--------|-------------|
| `/#/` | GET | Home page |
| `/#/login` | GET | Login page |
| `/#/register` | GET | Registration page |
| `/#/jobs` | GET | Jobs page (referenced in X-Recruiting header) |

## Input Points

### Authentication Endpoint (`POST /rest/user/login`)
- **Content-Type**: `application/json`
- **Fields**:
  - `email` (string) - User email address
  - `password` (string) - User password

### Registration Endpoint (`POST /rest/user/registration`)
- **Status**: Returns 500 error - not accessible via API
- **Expected fields** (based on Juice Shop patterns):
  - `email` (string)
  - `password` (string)
  - `name` (string)

### FTP File Server
- **File extension filter**: Only `.md` and `.pdf` files allowed
- **Directory traversal**: Possible via directory listing navigation
- **Search input**: Client-side search in directory listings

### Query Parameters
- `/#/login` - Angular hash route parameter
- `/#/register` - Angular hash route parameter

## Security Headers
- `Access-Control-Allow-Origin: *` - **CORS wide open**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Feature-Policy: payment 'self'`
- `X-Recruiting: /#/jobs` - **Information disclosure**
- **Missing**: Content-Security-Policy, X-XSS-Protection, Strict-Transport-Security

## ZAP Alerts Identified
1. **Cross-Domain Misconfiguration** (Medium) - `Access-Control-Allow-Origin: *`
2. **Content Security Policy Not Set** (Medium) - No CSP header
3. **Timestamp Disclosure** (Low) - Unix timestamps in CSS files
4. **Application Error Disclosure** (Low) - Stack traces in 500 errors
5. **Authentication Request Identified** - Login endpoint detected
6. **Information Disclosure - Sensitive Info in URL** - Credentials in query params
7. **Modern Web Application** - Cookie consent framework detected

## FTP Directory Contents (Sensitive Files)
- `acquisitions.md` - Contains confidential M&A information
- `announcement_encrypted.md` - Large encrypted file (369KB) with numeric strings
- `incident-support.kdbx` - KeePass password database
- `coupons_2013.md.bak` - Backup file (blocked by extension filter)
- `eastere.gg` - Game/data file (blocked by extension filter)
- `encrypt.pyc` - Python bytecode file (blocked by extension filter)
- `quarantine/` - Contains malware URL shortcuts pointing to GitHub

## Authentication Status
- **Registration**: NOT accessible (all paths return 500)
- **Login**: Endpoint exists at `POST /rest/user/login`
- **Default credentials tested**: Multiple variations tried, all returned 401 "Invalid email or password."
- **ZAP authentication**: Could NOT be set up - no valid credentials discovered
- **Known Juice Shop credentials attempted**:
  - `admin@juiceshop.local` / `admin123`, `admin`, `password`, `123456`, `password123`
  - `bender@juiceshop.local` / `HeyJude`
  - `user@juiceshop.local` / `password123`
  - `demouser@juiceshop.local` / `demouser`
  - `test@juiceshop.local` / `test123`
  - `administrator@juiceshop.local` / `admin123`
  - `webmaster@juiceshop.local` / `admin123`

## Key Findings
1. **CORS misconfiguration** - All endpoints return `Access-Control-Allow-Origin: *`
2. **No CSP** - No Content-Security-Policy header
3. **Stack trace disclosure** - 500 errors reveal full Express.js stack traces
4. **FTP directory listing** - Sensitive files accessible, extension filter present
5. **Encrypted announcement** - 369KB file with large numeric strings (possible encrypted data)
6. **KeePass database** - `incident-support.kdbx` accessible (3.2KB)
7. **Malware shortcuts** - Quarantine directory contains URL shortcuts to malicious executables
8. **Registration endpoint disabled** - Returns 500 on all tested paths
9. **Angular SPA** - Client-side routing with hash-based navigation
10. **X-Recruiting header** - Leaks internal job page URL