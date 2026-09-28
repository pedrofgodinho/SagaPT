# OWASP Juice Shop - Complete Attack Surface

## Technology Stack
- **Framework**: Node.js / Express ^4.22.1
- **Frontend**: Angular SPA (bundled JS: main.js, polyfills.js, scripts.js)
- **Database**: SQLite (confirmed from error stack traces referencing sequelize/sqlite)
- **ORM**: Sequelize
- **Auth**: JWT (RS256) returned in response body (not cookie)
- **File Server**: Express file server with .md/.pdf only restriction
- **CORS**: `Access-Control-Allow-Origin: *` (open to all origins)

## Authentication
- **Login Endpoint**: `POST /rest/user/login`
  - Body: `{ "email": "...", "password": "..." }`
  - Response: `{ "authentication": { "token": "eyJ..." }, "bid": 6, "umail": "..." }`
  - JWT returned in `authentication.token` field (Bearer token required for authenticated endpoints)
- **Registration Endpoint**: `POST /api/Users`
  - Body: `{ "email": "...", "password": "...", "securityAnswer": "...", "securityQuestion": <int> }`
  - Validation: email must be unique
- **Security Questions**: `GET /api/SecurityQuestions` (14 questions, publicly accessible)
  - Questions include: sibling middle name, mother's maiden name, birth dates, pet name, dentist name, zip code, company, book, movie, ID card number, hiking place

## Public API Endpoints (No Auth Required)

### Products
| Endpoint | Method | Input Parameters | Response Fields |
|----------|--------|-----------------|-----------------|
| `/api/Products` | GET | `searchTerm` (query param) | `id`, `name`, `description`, `price`, `deluxePrice`, `image`, `createdAt`, `updatedAt`, `deletedAt` |
| `/rest/products/search` | GET | `searchTerm` (query param) | Same as above |

### Feedbacks
| Endpoint | Method | Input Parameters | Response Fields |
|----------|--------|-----------------|-----------------|
| `/api/Feedbacks` | GET | None | `UserId`, `id`, `comment`, `rating`, `createdAt`, `updatedAt` |

### Security Questions
| Endpoint | Method | Input Parameters | Response Fields |
|----------|--------|-----------------|-----------------|
| `/api/SecurityQuestions` | GET | None | `id`, `question`, `createdAt`, `updatedAt` |

### User Registration
| Endpoint | Method | Input Parameters | Response Fields |
|----------|--------|-----------------|-----------------|
| `/api/Users` | POST | `email`, `password`, `securityAnswer`, `securityQuestion` | N/A (validation errors) |

### User Login
| Endpoint | Method | Input Parameters | Response Fields |
|----------|--------|-----------------|-----------------|
| `/rest/user/login` | POST | `email`, `password` | `authentication.token`, `bid`, `umail` |

## Authenticated API Endpoints (JWT Bearer Required)

### Basket
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|-----------------|-------|
| `/api/BasketItems` | GET | None | Returns 401 without auth |
| `/api/BasketItems` | POST | `productId`, `quantity` | Returns 401 without auth |

### Complaints
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|-----------------|-------|
| `/api/Complaints` | GET | None | Returns 401 without auth |
| `/api/Complaints` | POST | `message` | Returns 401 without auth |

### Feedbacks (POST)
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|-----------------|-------|
| `/api/Feedbacks` | POST | `rating`, `comment`, `captchaId` | Returns 500 without captchaId (SQL WHERE clause error) |

### Users
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|-----------------|-------|
| `/api/Users/1` | GET | N/A (user ID in path) | Returns 401 without auth |

### Orders
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|-----------------|-------|
| `/api/Orders` | GET | None | Returns 500 "Unexpected path" - may not exist |

## Static File Endpoints

### FTP Directory (Public)
| Endpoint | Method | Notes |
|----------|--------|-------|
| `/ftp/` | GET | Directory listing - contains sensitive files |
| `/ftp/acquisitions.md` | GET | Confidential acquisition plans |
| `/ftp/suspicious_errors.yml` | GET | 403 - Only .md and .pdf allowed |
| `/ftp/coupons_2013.md.bak` | GET | Backup file with coupons |
| `/ftp/announce_encrypted.md` | GET | Encrypted announcement |
| `/ftp/eastere.gg` | GET | Easter egg file |
| `/ftp/encrypt.pyc` | GET | 403 - Only .md and .pdf allowed |
| `/ftp/incident-support.kdbx` | GET | 403 - Only .md and .pdf allowed |
| `/ftp/legal.md` | GET | Legal document |
| `/ftp/quarantine/` | GET | Directory with malware URL files |
| `/ftp/package.json.bak` | GET | Backup package.json |
| `/ftp/package-lock.json.bak` | GET | Backup package-lock.json |

### SPA Assets
| Endpoint | Method | Notes |
|----------|--------|-------|
| `/` | GET | Main Angular SPA |
| `/main.js` | GET | Main bundled JS (1.2MB) |
| `/polyfills.js` | GET | Angular polyfills |
| `/scripts.js` | GET | App scripts |
| `/styles.css` | GET | Stylesheet |
| `/sitemap.xml` | GET | Sitemap |
| `/robots.txt` | GET | Disallows /ftp |

## Input Points Checklist

### Query String Parameters
- `searchTerm` on `/api/Products` and `/rest/products/search`

### POST JSON Body Fields
- **Registration** (`POST /api/Users`): `email`, `password`, `securityAnswer`, `securityQuestion`
- **Login** (`POST /rest/user/login`): `email`, `password`
- **Basket** (`POST /api/BasketItems`): `productId`, `quantity`
- **Feedback** (`POST /api/Feedbacks`): `rating`, `comment`, `captchaId`
- **Complaint** (`POST /api/Complaints`): `message`

### URL Path Parameters
- User ID in `/api/Users/{id}` (e.g., `/api/Users/1`)

### File Upload Paths
- `/ftp/` directory - file extension filtering (.md, .pdf only)

## Security Headers Observed
- `X-Content-Type-Options: nosniff` ✓
- `X-Frame-Options: SAMEORIGIN` ✓
- `Feature-Policy: payment 'self'` ✓
- `Access-Control-Allow-Origin: *` ⚠️ (CORS wide open)
- CSP header: NOT SET ⚠️

## Known Vulnerabilities/Interesting Findings
1. **Information Disclosure**: Error pages reveal Express version, file paths, Sequelize/SQLite internals
2. **CORS Misconfiguration**: Open CORS policy (`Access-Control-Allow-Origin: *`)
3. **Missing CSP**: No Content-Security-Policy header
4. **Sensitive Files in FTP**: acquisitions.md (confidential plans), backup files (.bak), encrypted files
5. **JWT in Response Body**: Token returned in JSON body, not as HttpOnly cookie
6. **Timestamp Disclosure**: Unix timestamps in CSS files and API responses
7. **SQL Error Disclosure**: 500 errors reveal Sequelize query structure
8. **File Extension Filter**: Only .md and .pdf allowed in /ftp/ (potential bypass)
9. **Captcha Dependency**: Feedback POST requires captchaId (missing causes SQL error)
10. **X-Recruiting Header**: Points to `/#/jobs` route

## Authenticated Endpoint Access
- ZAP context configured with credentials (test@test.com / testtest123)
- JWT token: `eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...` (in login_test_user_raw.json)
- Note: Authenticated endpoints require Bearer token in Authorization header
- ZAP form-based auth may not automatically attach JWT (returned in body, not cookie)
- DAST agent should include `Authorization: Bearer <token>` header for authenticated tests