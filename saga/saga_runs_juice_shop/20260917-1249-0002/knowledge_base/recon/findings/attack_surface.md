# Attack Surface - OWASP Juice Shop (http://juiceshop.local:3000)

## Technology Stack
- **Framework**: Node.js with Express ^4.22.1
- **Frontend**: Angular (SPA with hash-based routing)
- **Server**: Node.js/Express
- **Content-Type**: HTML/JavaScript/CSS served from static assets
- **CORS**: Access-Control-Allow-Origin: * (permissive, all origins allowed)
- **Security Headers Present**: X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Feature-Policy: payment 'self'
- **Missing Headers**: No Content-Security-Policy header

## Discovered Endpoints

### Static Assets & Files
| Method | Path | Description |
|--------|------|-------------|
| GET | / | Main homepage (Angular SPA) |
| GET | /robots.txt | Disallows /ftp (28 bytes) |
| GET | /sitemap.xml | Returns homepage HTML (not XML) |
| GET | /main.js | Main JavaScript bundle (1.2MB) |
| GET | /polyfills.js | Angular polyfills |
| GET | /scripts.js | Application scripts |
| GET | /styles.css | Stylesheet with timestamp disclosure |
| GET | /assets/public/favicon_js.ico | Favicon |
| GET | /ftp/ | FTP directory listing (directory traversal enabled) |
| GET | /ftp/acquisitions.md | Confidential acquisition plans (909 bytes) |
| GET | /ftp/legal.md | Legal information / Terms of Use (3047 bytes) |
| GET | /ftp/incident-support.kdbx | KeePass database file (3246 bytes, binary) |
| GET | /ftp/announcement_encrypted.md | Large encrypted announcement (369KB) |
| GET | /ftp/coupons_2013.md.bak | Backup file - returns 403 "Only .md and .pdf files are allowed!" |
| GET | /ftp/eastere.gg | Easter egg file (324 bytes) |
| GET | /ftp/encrypt.pyc | Python bytecode file |
| GET | /ftp/quarantine/ | Quarantine directory with malware URL files |
| GET | /ftp/quarantine/juicy_malware_macos_64.url | Malware URL file |
| GET | /ftp/quarantine/juicy_malware_linux_amd_64.url | Malware URL file |
| GET | /ftp/quarantine/juicy_malware_linux_arm_64.url | Malware URL file |
| GET | /ftp/quarantine/juicy_malware_windows_64.exe.url | Malware URL file |

### Angular Routes (SPA)
| Method | Path | Description |
|--------|------|-------------|
| GET | /#/login | Login page |
| GET | /#/registration | Registration page |
| GET | /#/admin | Admin panel |
| GET | /#/jobs | Jobs page (referenced in X-Recruiting header) |
| GET | /#/ | Home/Shop page |
| GET | /#/basket | Shopping basket |
| GET | /#/delivery | Delivery page |
| GET | /#/payment | Payment page |
| GET | /#/profile | User profile |
| GET | /#/search | Search functionality |
| GET | /#/admin/users | Admin user management |
| GET | /#/admin/configuration | Admin configuration |

### Authentication Endpoints (REST)
| Method | Path | Status | Input Parameters |
|--------|------|--------|------------------|
| POST | /rest/user/login | Returns 401 "Invalid email or password" | email (string), password (string) |
| GET | /rest/user/login | Returns 500 | - |
| POST | /rest/user/registration | Returns 500 "Unexpected path" | email, password, nickname |
| GET | /rest/user/registration | Returns 500 | - |
| POST | /rest/user/register | Returns 500 | email, password, nickname |
| POST | /rest/user/signup | Returns 500 | email, password, nickname |

### API Endpoints (Attempted - all return 500)
| Method | Path | Status |
|--------|------|--------|
| GET | /api/v1/rest/products | 500 "Unexpected path" |
| GET | /api/v1/rest/users | 500 "Unexpected path" |
| GET | /api/v1/rest/orders | 500 "Unexpected path" |
| GET | /api/v1/rest/admin/configuration | 500 "Unexpected path" |
| GET | /api/v1/rest/user/registration | 500 "Unexpected path" |
| GET | /api/v1/rest/user/login | 500 "Unexpected path" |
| GET | /api/v1/rest/products/1 | 500 "Unexpected path" |
| GET | /rest/products | 500 "Unexpected path" |
| GET | /rest/users/me | 500 "Unexpected path" |
| GET | /rest/orders | 500 "Unexpected path" |
| GET | /rest/admin/configuration | 500 "Unexpected path" |

### Admin/Common Paths (Attempted)
| Method | Path | Status |
|--------|------|--------|
| GET | /admin | Returns homepage (Angular SPA catches it) |
| GET | /administrator | Returns homepage |
| GET | /dashboard | Returns homepage |
| GET | /api/v1/users | 500 "Unexpected path" |
| GET | /api/v1/products | 500 "Unexpected path" |
| GET | /api/v1/orders | 500 "Unexpected path" |
| GET | /api/v1/admin/configuration | 500 "Unexpected path" |

### FTP File Server
| Method | Path | Description |
|--------|------|-------------|
| GET | /ftp/* | File download endpoint - only allows .md and .pdf extensions |
| GET | /ftp/\* | Returns 403 for non-.md/.pdf files |

## Input Points

### Query Parameters (Angular Routes)
- Angular hash-based routing: `/#/page?param=value`
- Search functionality likely accepts query parameters

### Form Fields (Login)
- `email` - text input
- `password` - password input

### Form Fields (Registration)
- `email` - text input
- `password` - password input
- `nickname` - text input
- `securityQuestion` - numeric (question ID)
- `securityAnswer` - text input

### POST Request Bodies
- `/rest/user/login` - JSON: `{email, password}`
- `/rest/user/registration` - JSON: `{email, password, nickname}`

### Headers
- `Content-Type` - application/json for API calls
- Cookie-based authentication (session cookies)
- Authorization header for authenticated requests

### File Upload/Input
- FTP file server accepts .md and .pdf files
- Directory traversal possible via /ftp/ path

## Security Observations
1. **CORS Misconfiguration**: `Access-Control-Allow-Origin: *` allows any origin
2. **Missing CSP**: No Content-Security-Policy header
3. **Timestamp Disclosure**: Unix timestamps in styles.css
4. **Information Disclosure**: Stack traces visible in 500 errors (Express paths shown)
5. **Directory Listing**: /ftp/ exposes sensitive files
6. **Sensitive Files Exposed**: acquisitions.md (confidential), incident-support.kdbx (password database), encrypted announcement
7. **File Extension Filter Bypass Attempt**: /ftp/coupons_2013.md.bak returns 403
8. **SPA Routing**: Angular hash-based routing (#/) for all client-side navigation
9. **Authentication**: Form-based login with email/password, ZAP user registered (user_id: 256)
10. **X-Recruiting Header**: Points to /#/jobs endpoint

## Credentials
- Test account registered: test@test.com / Test1234! (user_id: 256, registered via ZAP context)
- Authentication context configured for ZAP forced user mode
