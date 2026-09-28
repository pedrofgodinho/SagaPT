# Attack Surface - OWASP Juice Shop

## Application Overview
- **Target:** http://juiceshop.local:3000
- **Application:** OWASP Juice Shop (deliberately vulnerable web app)
- **Spider discovered:** 66 URLs

## Technology Stack
- **Frontend:** Angular (SPA with hash-based routing: `/#/login`, `/#/register`, `/#/jobs`)
- **Backend:** Node.js with Express ^4.22.1
- **UI Framework:** Angular Material (bluegrey-lightgreen-theme)
- **Fonts:** VT323, Roboto
- **Authentication:** Form-based, JWT token via Authorization header

## Registered Credentials
- **Username:** recon_test_user
- **Password:** TestPass123!
- **Email:** recon@test.com
- **User ID:** 25 (API), 168 (ZAP context)

## Discovered Endpoints & Input Points

### REST API Endpoints (Base: `/api/`)
| Method | Endpoint | Auth Required | Description | Input Parameters |
|--------|----------|---------------|-------------|------------------|
| GET | `/api/Products` | No | List all products | None |
| GET | `/api/Products/:id` | No | Get single product | `:id` (path param) |
| POST | `/api/Users` | No | Register new user | `username`, `password`, `email`, `securityQuestion` (id, answer), `address` (array: street, city, state, zipCode, phone) |
| GET | `/api/Users` | Yes | List users | None (401 without auth) |
| POST | `/api/Users/login` | No | User login | `email`, `password` |
| GET | `/api/SecurityQuestions` | No | List security questions | None |
| GET | `/api/SecurityQuestions/:id` | No | Get specific security question | `:id` (path param) |

### GraphQL Endpoint
| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/graphql` | ? | GraphQL interface (Angular SPA routing) |

### SPA Hash Routes
| Route | Description |
|-------|-------------|
| `/#/login` | Login page |
| `/#/register` | Registration page |
| `/#/jobs` | Jobs/recruitment page (referenced in `X-Recruiting` header) |
| `/#/recycle` | Recycling page (referenced in product descriptions) |

### Static File Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/styles.css` | Main stylesheet |
| GET | `/main.js` | Angular app bundle |
| GET | `/polyfills.js` | Browser polyfills |
| GET | `/scripts.js` | Application scripts |
| GET | `/assets/public/` | Public assets directory |

### FTP Directory (Publicly Accessible)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ftp/` | Directory listing |
| GET | `/ftp/acquisitions.md` | Confidential acquisitions document |
| GET | `/ftp/announcement_encrypted.md` | Encrypted announcement (369KB) |
| GET | `/ftp/coupons_2013.md.bak` | Backup file with coupons |
| GET | `/ftp/eastere.gg` | Easter egg file |
| GET | `/ftp/encrypt.pyc` | Python compiled file |
| GET | `/ftp/incident-support.kdbx` | KeePass password database |
| GET | `/ftp/legal.md` | Legal document |
| GET | `/ftp/quarantine/` | Subdirectory with malware samples |
| GET | `/ftp/quarantine/juicy_malware_macos_64.url` | macOS malware URL |
| GET | `/ftp/quarantine/juicy_malware_linux_amd_64.url` | Linux malware URL |
| GET | `/ftp/quarantine/juicy_malware_linux_arm_64.url` | Linux ARM malware URL |
| GET | `/ftp/quarantine/juicy_malware_windows_64.exe.url` | Windows malware URL |

### Configuration/Discovery Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/robots.txt` | Disallows `/ftp` |
| GET | `/sitemap.xml` | Returns SPA page (not actual sitemap) |

### Non-functional Endpoints (return 500 errors)
| Method | Endpoint |
|--------|----------|
| GET | `/api/v1/users` |
| GET | `/api/v1/products` |
| GET | `/api/v1/security-question` |
| GET | `/api/v1/` |
| GET | `/api/Categories` |
| GET | `/api/Orders` |
| GET | `/api/Feedback` |
| GET | `/api/Uri` |
| GET | `/rest/user/me` |
| POST | `/rest/user/signup` |

## Key Input Points Summary
- **Form fields:** `username`, `password`, `email`, `securityQuestion.id`, `securityQuestion.answer`, `address.street`, `address.city`, `address.state`, `address.zipCode`, `address.phone`
- **Path parameters:** `Products/:id`, `SecurityQuestions/:id`, `Users/:id`
- **Query parameters:** None discovered yet
- **HTTP headers:** `Authorization` (Bearer token), `Content-Type` (application/json)

## Security-Relevant Headers
- `Access-Control-Allow-Origin: *` (CORS wildcard)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Feature-Policy: payment 'self'`
- `X-Recruiting: /#/jobs` (information disclosure)
- No `Content-Security-Policy` header