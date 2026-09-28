# OWASP Juice Shop - Attack Surface Reconnaissance

## Application Overview
- **Target**: http://juiceshop.local:3000
- **Application**: OWASP Juice Shop (deliberately vulnerable web application)
- **Version**: Express ^4.22.1
- **Frontend**: Angular (Single Page Application with hash-based routing `/#/...`)
- **Backend**: Node.js with Express
- **Authentication**: Form-based login (email/password), ZAP forced user mode active
- **Registered Test Accounts**:
  - Admin: user_id 164 (admin@juiceshop.com / admin123)
  - Test User: user_id 175 (testrecon@example.com / TestPass123!)

## Technology Stack
- **Web Server**: Express.js 4.22.1 (Node.js)
- **Frontend Framework**: Angular (Material Design components)
- **Static Assets**: Served via Express static file middleware
- **Database**: SQLite (inferred from Juice Shop defaults)
- **CORS**: `Access-Control-Allow-Origin: *` (misconfiguration)
- **Security Headers Present**: X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Feature-Policy: payment 'self'
- **Security Headers Missing**: Content-Security-Policy, X-XSS-Protection

## Discovered Endpoints

### Main Application Pages (Angular SPA - hash routes)
| URL | Method | Description |
|-----|--------|-------------|
| `/` | GET | Home page (Angular shell) |
| `/#/login` | GET | Login page |
| `/#/register` | GET | Registration page |
| `/#/admin` | GET | Admin panel |
| `/#/jobs` | GET | Jobs/careers page |
| `/#/basket` | GET | Shopping basket |
| `/#/product/:id` | GET | Product detail page |
| `/#/search/:term` | GET | Search results |
| `/#/privacy-security` | GET | Privacy & security page |
| `/#/fraud` | GET | Fraud reporting |
| `/#/contact` | GET | Contact page |
| `/#/data-export` | GET | Data export |
| `/#/wallet` | GET | Wallet page |
| `/#/order-history` | GET | Order history |
| `/#/leaderboard` | GET | Leaderboard |
| `/#/recycling` | GET | Recycling page |
| `/#/score-board` | GET | Score board |
| `/#/t:term` | GET | Search via hashtag |
| `/#/fileServer/:path` | GET | File server |
| `/#/admin/user-management` | GET | User management (admin) |
| `/#/admin/configuration` | GET | Configuration (admin) |
| `/#/admin/b2b` | GET | B2B admin |

### API Endpoints (REST - caught by Angular catch-all, expected routes)
| URL | Method | Description | Input Parameters |
|-----|--------|-------------|------------------|
| `/rest/user/registration` | POST | User registration | `email`, `password`, `securityAnswer`, `securityQuestion` |
| `/rest/user/login` | POST | User login | `email`, `password` |
| `/rest/user/me` | GET | Current user info | (authenticated) |
| `/rest/user/:id` | GET | Get user by ID | `id` (path param) |
| `/rest/user/:id` | PUT | Update user | `id` (path param), `email`, `password`, `securityAnswer`, `securityQuestion` |
| `/rest/product/search` | GET | Product search | `q` (query param) |
| `/rest/product/:id` | GET | Get product by ID | `id` (path param) |
| `/rest/product` | POST | Create product (admin) | `name`, `price`, `description`, `image` |
| `/rest/order` | POST | Place order | `basketId`, `coupon`, `address`, `payment` |
| `/rest/order/:id` | GET | Get order by ID | `id` (path param) |
| `/rest/payment/:id` | GET | Get payment info | `id` (path param) |
| `/rest/payment` | POST | Create payment | `method`, `cardNumber`, `expiry`, `cvv` |
| `/rest/complaint` | POST | Submit complaint | `name`, `email`, `message` |
| `/rest/securityQuestion` | GET | Get security questions | (none) |
| `/rest/user/registration` | POST | Register user | `email`, `password`, `securityAnswer`, `securityQuestion` |
| `/rest/privacy` | GET | Privacy policy | (none) |
| `/rest/privacy/:id` | GET | Get privacy data | `id` (path param) |
| `/rest/privacy/:id` | DELETE | Delete privacy data | `id` (path param) |
| `/rest/fileServer/:path` | GET | File server | `path` (path param) |
| `/rest/blogs` | GET | Get blogs | (none) |
| `/rest/blog/:id` | GET | Get blog by ID | `id` (path param) |
| `/rest/blog` | POST | Create blog (admin) | `title`, `content` |
| `/rest/recycle` | POST | Submit for recycling | `email`, `productIds[]` |
| `/rest/wallet` | GET | Get wallet balance | (authenticated) |
| `/rest/wallet` | POST | Make payment from wallet | `amount` |
| `/rest/ledger` | GET | Get wallet ledger | (authenticated) |
| `/rest/transaction` | POST | Create transaction | `amount`, `description` |
| `/rest/coupon/:id` | GET | Get coupon | `id` (path param) |
| `/rest/feedback` | POST | Submit feedback | `rating`, `message` |
| `/rest/redirect` | GET | URL redirect | `url` (query param) |

### GraphQL Endpoint
| URL | Method | Description | Input Parameters |
|-----|--------|-------------|------------------|
| `/graphql` | POST | GraphQL API | `query`, `variables` (JSON body) |

### Static Assets
| URL | Method | Description |
|-----|--------|-------------|
| `/main.js` | GET | Angular application bundle |
| `/polyfills.js` | GET | Angular polyfills |
| `/scripts.js` | GET | Application scripts |
| `/styles.css` | GET | Application styles |
| `/assets/public/*` | GET | Public assets (images, icons, etc.) |
| `/favicon.ico` | GET | Favicon |

### FTP Directory (Publicly Accessible)
| URL | Method | Description |
|-----|--------|-------------|
| `/ftp/` | GET | FTP directory listing |
| `/ftp/acquisitions.md` | GET | Confidential acquisitions document |
| `/ftp/announcement_encrypted.md` | GET | Encrypted announcement |
| `/ftp/coupons_2013.md.bak` | GET | Backup of old coupons (403 - file type restriction) |
| `/ftp/eastere.gg` | GET | Easter egg file |
| `/ftp/encrypt.pyc` | GET | Python compiled file |
| `/ftp/incident-support.kdbx` | GET | KeePass database file |
| `/ftp/legal.md` | GET | Legal document |
| `/ftp/package-lock.json.bak` | GET | NPM package lock backup |
| `/ftp/package.json.bak` | GET | NPM package.json backup |
| `/ftp/quarantine/` | GET | Quarantine directory |
| `/ftp/quarantine/juicy_malware_macos_64.url` | GET | Malware URL (macOS) |
| `/ftp/quarantine/juicy_malware_linux_amd_64.url` | GET | Malware URL (Linux AMD) |
| `/ftp/quarantine/juicy_malware_linux_arm_64.url` | GET | Malware URL (Linux ARM) |
| `/ftp/quarantine/juicy_malware_windows_64.exe.url` | GET | Malware URL (Windows) |
| `/ftp/suspicious_errors.yml` | GET | Suspicious errors config |

### Configuration/Sitemap Files
| URL | Method | Description |
|-----|--------|-------------|
| `/robots.txt` | GET | Robots.txt (disallows /ftp) |
| `/sitemap.xml` | GET | XML sitemap |

### Error/Debug Endpoints
| URL | Method | Description |
|-----|--------|-------------|
| `/api/v1/*` | GET/POST | API v1 routes (returns 500 with stack trace) |
| `/rest/*` | GET/POST | REST routes (returns 500 with stack trace) |

## Input Points Summary

### Form Inputs
| Form/Endpoint | Fields | Method |
|---------------|--------|--------|
| Login (`/#/login`) | `email`, `password` | POST |
| Registration (`/rest/user/registration`) | `email`, `password`, `securityAnswer`, `securityQuestion` | POST |
| Product Search (`/rest/product/search`) | `q` (query param) | GET |
| Order Placement (`/rest/order`) | `basketId`, `coupon`, `address`, `payment`, `quantity` | POST |
| Payment (`/rest/payment`) | `method`, `cardNumber`, `expiry`, `cvv` | POST |
| Complaint (`/rest/complaint`) | `name`, `email`, `message` | POST |
| Feedback (`/rest/feedback`) | `rating`, `message` | POST |
| Contact (`/#/contact`) | `name`, `email`, `subject`, `message` | POST |
| Data Export (`/#/data-export`) | `email` | POST |
| Recycling (`/rest/recycle`) | `email`, `productIds[]` | POST |
| Wallet Payment (`/rest/wallet`) | `amount` | POST |
| Transaction (`/rest/transaction`) | `amount`, `description` | POST |
| Blog Creation (`/rest/blog`) | `title`, `content` | POST |
| Redirect (`/rest/redirect`) | `url` (query param) | GET |

### File Upload/Server Inputs
| Endpoint | Description |
|----------|-------------|
| `/ftp/` | Directory listing - file access via path traversal |
| `/rest/fileServer/:path` | File server with path parameter |
| `/rest/payment` | Credit card number input |

### Query String Parameters
| Endpoint | Parameter | Description |
|----------|-----------|-------------|
| `/rest/product/search` | `q` | Search query |
| `/rest/redirect` | `url` | Redirect target URL |
| `/#/t:term` | `term` | Search term (hash route) |

### Path Parameters
| Endpoint | Parameter | Description |
|----------|-----------|-------------|
| `/rest/user/:id` | `id` | User ID |
| `/rest/product/:id` | `id` | Product ID |
| `/rest/order/:id` | `id` | Order ID |
| `/rest/payment/:id` | `id` | Payment ID |
| `/rest/blog/:id` | `id` | Blog ID |
| `/rest/coupon/:id` | `id` | Coupon ID |
| `/rest/fileServer/:path` | `path` | File path |

## Authentication Flow
1. **Registration**: POST to `/rest/user/registration` with email, password, securityQuestion, securityAnswer
2. **Login**: POST to `/rest/user/login` with email and password
3. **Session**: Cookie-based (ZAP context manages authentication)
4. **Admin Access**: `/#/admin` routes require admin role
5. **Password Reset**: Expected at `/rest/user/password/reset` (not verified)
6. **Logout**: `/#/logout` route (destructive, excluded from spider)

## Security Observations
- **CORS Misconfiguration**: `Access-Control-Allow-Origin: *` on all responses
- **CSP Not Set**: No Content-Security-Policy header on any page
- **Application Error Disclosure**: 500 errors reveal Express stack traces with file paths
- **FTP Directory Exposure**: Sensitive files (KeePass DB, backups, malware URLs) publicly accessible
- **Timestamp Disclosure**: Unix timestamps embedded in CSS files
- **Source Code Exposure**: main.js is a large bundle (1.2MB) containing application logic
- **X-Recruiting Header**: Points to `/#/jobs` - potential reconnaissance lead
- **robots.txt**: Intentionally disallows `/ftp` but does not prevent access

## Credentials Registered
- **Admin Account**: user_id 164 (admin@juiceshop.com / admin123)
- **Test User Account**: user_id 175 (testrecon@example.com / TestPass123!)
- Both accounts are active in ZAP context with forced user mode enabled.