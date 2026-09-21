# OWASP Juice Shop - Attack Surface Map

## Technology Stack
- **Backend**: Node.js / Express.js (^4.22.1)
- **Frontend**: Angular SPA (hash-based routing `/#/`, Material Design)
- **Database**: SQLite (inferred from Sequelize ORM usage)
- **Framework**: OWASP Juice Shop (deliberately vulnerable application)

## Security Headers Observed
- `X-Content-Type-Options: nosniff` ✓
- `X-Frame-Options: SAMEORIGIN` ✓
- `Feature-Policy: payment 'self'` ✓
- `Access-Control-Allow-Origin: *` (wide open CORS) ⚠
- **Missing**: Content-Security-Policy (CSP) ⚠

---

## Discovered Endpoints

### Public API Endpoints (No Auth Required)

| Method | Endpoint | Input Parameters | Response |
|--------|----------|-----------------|----------|
| GET | `/` | - | SPA shell (Angular) |
| GET | `/api/Products` | `search`, `limit`, `offset`, `orderBy` | JSON product list |
| GET | `/api/Products/{id}` | `{id}` path param | JSON product detail |
| GET | `/api/SecurityQuestions` | - | JSON array of 14 security questions |
| GET | `/rest/user/whoami` | - | `{"user":{}}` |
| GET | `/robots.txt` | - | `Disallow: /ftp` |
| GET | `/sitemap.xml` | - | Returns SPA shell |
| GET | `/graphql` | - | Returns SPA shell |

### Authentication Endpoints

| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| POST | `/rest/user/login` | `email`, `password` (JSON body) | Returns 401 "Invalid email or password." |
| POST | `/rest/user/signup` | `email`, `password`, `securityAnswer`, `securityQuestion` | **500 Error** - endpoint not found (may be SPA-only) |
| GET | `/#/login` | - | Angular SPA route |
| GET | `/#/signup` | - | Angular SPA route |

### Auth-Protected API Endpoints (Require Bearer Token)

| Method | Endpoint | Input Parameters | Auth Required |
|--------|----------|-----------------|---------------|
| GET | `/api/Users` | - | Yes (401 without token) |
| GET | `/api/PrivacyRequests` | - | Yes (401 without token) |

### Potential Auth-Protected Endpoints (Not Verified)
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET/POST | `/api/Order` | Returned 500 "Unexpected path" |
| GET/POST | `/api/Feedback` | Returned 500 "Unexpected path" |
| GET/POST | `/api/Cart` / `/api/Basket` | Returned 500 "Unexpected path" |
| GET/POST | `/api/Coupon` | Returned 500 "Unexpected path" |
| GET/POST | `/api/Address` | Returned 500 "Unexpected path" |
| GET/POST | `/api/Webhooks` | Returned 500 "Unexpected path" |
| GET/POST | `/api/User` | Returned 500 "Unexpected path" |
| GET/POST | `/api/Product` | Returned 500 "Unexpected path" |
| GET/POST | `/api/SecurityQuestion` | Returned 500 "Unexpected path" |
| GET/POST | `/api/PrivacyRequest` | Returned 500 "Unexpected path" |
| GET/POST | `/rest/Order` | Returned 500 "Unexpected path" |
| GET/POST | `/rest/Product` | Returned 500 "Unexpected path" |
| GET/POST | `/rest/Feedback` | Returned 500 "Unexpected path" |
| GET/POST | `/rest/Coupon` | Returned 500 "Unexpected path" |
| GET/POST | `/rest/User/signup` | Returned 500 "Unexpected path" |
| GET/POST | `/rest/user/register` | Returned 500 "Unexpected path" |

### File Server / FTP Directory

| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/ftp/` | Directory listing (public) |
| GET | `/ftp/acquisitions.md` | "Planned Acquisitions" - confidential doc |
| GET | `/ftp/legal.md` | Terms of Use |
| GET | `/ftp/suspicious_errors.yml` | 403 - only .md and .pdf allowed |
| GET | `/ftp/coupons_2013.md.bak` | Backup file |
| GET | `/ftp/encrypt.pyc` | 403 - only .md and .pdf allowed |
| GET | `/ftp/announcement_encrypted.md` | Encrypted announcement |
| GET | `/ftp/` | Contains `quarantine/` subdirectory |

### Static Assets

| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/main.js` | Angular bundle (1.2MB) |
| GET | `/scripts.js` | Cookie consent script |
| GET | `/polyfills.js` | Angular polyfills |
| GET | `/styles.css` | CSS with timestamp disclosure |
| GET | `/assets/public/favicon_js.ico` | Favicon |

---

## Input Points Summary

### Query String Parameters
- `search` - Product search (API)
- `limit` - Pagination limit (API)
- `offset` - Pagination offset (API)
- `orderBy` - Sort field (API)

### POST JSON Body Fields
- `email` - Login/signup email
- `password` - Login/signup password
- `securityAnswer` - Security question answer (signup)
- `securityQuestion` - Security question ID (signup)

### SPA Routes (Angular client-side)
- `/#/login` - Login page
- `/#/signup` - Registration page
- `/#/jobs` - Jobs page (referenced in X-Recruiting header)
- `/#/recycle` - Recycling page (referenced in product description)
- `/#/privacy` - Privacy page (implied)
- `/#/admin` - Admin page (implied)
- `/#/admin/configuration` - Admin config (implied)
- `/#/admin/security` - Admin security (implied)
- `/#/admin/users` - Admin users (implied)
- `/#/score-board` - Scoreboard (implied)
- `/#/leader-board` - Leaderboard (implied)
- `/#/basket` - Shopping basket (implied)
- `/#/order` - Order history (implied)
- `/#/wallet` - Wallet (implied)
- `/#/coupon` - Coupon page (implied)
- `/#/delivery` - Delivery settings (implied)
- `/#/settings` - User settings (implied)
- `/#/profile` - User profile (implied)
- `/#/security-question` - Security question management (implied)
- `/#/data-export` - Data export (implied)
- `/#/privacy-security` - Privacy & security (implied)
- `/#/redemption` - Coupon redemption (implied)
- `/#/contact` - Contact form (implied)
- `/#/security` - Security info (implied)
- `/#/about` - About page (implied)
- `/#/imprint` - Imprint page (implied)
- `/#/jobs` - Jobs page (implied)
- `/#/recycle` - Recycling page (implied)
- `/#/safety` - Safety page (implied)
- `/#/42` - Easter egg page (implied)

### File Upload Points
- `/ftp/` directory - File server with extension filtering (only `.md` and `.pdf` allowed)

---

## Key Observations
1. **CORS is wide open** (`Access-Control-Allow-Origin: *`) on all endpoints
2. **No CSP header** set on any endpoint
3. **Timestamp disclosure** in CSS files (Unix timestamps)
4. **Application error disclosure** - stack traces visible in 500 errors
5. **Directory listing enabled** on `/ftp/`
6. **Backup files exposed** in `/ftp/` (`.bak` files)
7. **Confidential documents** accessible via `/ftp/` (acquisitions.md)
8. **Registration endpoint** appears to be SPA-only (no REST signup found)
9. **All API responses** follow `{"status":"success","data":...}` pattern
10. **Product API** supports `search`, `orderBy`, `limit`, `offset` parameters
11. **14 security questions** available via `/api/SecurityQuestions`
12. **Known default credentials** to test: `admin@example.com` / `admin123`, `admin@example.com` / `+JuicyAdmin+`