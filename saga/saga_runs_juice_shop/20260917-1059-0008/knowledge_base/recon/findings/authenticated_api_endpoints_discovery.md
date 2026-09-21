# Authenticated API Endpoints - Thorough Discovery Pass

## Discovery Method
- Auth registered: test@example.com / Test1234! (user_id: 299)
- ZAP forced user mode enabled for authenticated requests
- Spider + individual http_get probes against 30+ endpoints

## Endpoints Tested & Results

### ✅ Working Public Endpoints
| Method | Endpoint | Status | Notes |
|--------|----------|--------|-------|
| GET | /api/products | 200 | Returns 30+ products (id, name, description, price, deluxePrice, image, timestamps) |
| GET | /api/products/1 | 200 | Single product (Apple Juice) |
| GET | /api/products/2 | 200 | Single product (Orange Juice) |
| GET | /api/products/3 | 200 | Single product (Eggfruit Juice) |
| GET | /api/securityQuestions | 200 | 14 security questions (IDs 1-14) |

### 🔒 Auth-Required Endpoints (401 Unauthorized)
| Method | Endpoint | Status | Notes |
|--------|----------|--------|-------|
| GET | /rest/basket | 401 | "No Authorization header was found" |
| GET | /rest/basket/1 | 401 | Same auth error |
| GET | /rest/basket/1/product/1 | 401 | Same auth error |
| GET | /api/users/current | 401 | "No Authorization header was found" |
| GET | /api/users | 401 | "No Authorization header was found" |
| GET | /api/privacyRequests | 401 | "No Authorization header was found" |
| GET | /api/privacyRequests/1 | 401 | "No Authorization header was found" |

### ❌ Non-existent Endpoints (500 Internal Server Error)
These endpoints return 500 with full Express stack traces (error disclosure vulnerability):
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | /api/feedback | "Unexpected path: /api/feedback" |
| GET | /api/notifications | "Unexpected path: /api/notifications" |
| GET | /api/order | "Unexpected path: /api/order" |
| GET | /api/order/1 | "Unexpected path: /api/order/1" |
| GET | /rest/product/feedback/1 | "Unexpected path: /rest/product/feedback/1" |
| GET | /rest/payment | "Unexpected path: /rest/payment" |
| GET | /rest/payment/1 | "Unexpected path: /rest/payment/1" |
| GET | /rest/securityAnswer | "Unexpected path: /rest/securityAnswer" |
| GET | /rest/user/userAddress/1 | "Unexpected path: /rest/user/userAddress/1" |
| GET | /rest/user/creditCard/1 | "Unexpected path: /rest/user/creditCard/1" |
| GET | /api/consent | "Unexpected path: /api/consent" |
| GET | /api/consent/1 | "Unexpected path: /api/consent/1" |

### 📍 SPA Hash Routes (all return 200 HTML - Angular shell)
| Route | Notes |
|-------|-------|
| /#/product/1 | Angular SPA shell |
| /#/product/2 | Angular SPA shell |
| /#/admin | Angular SPA shell (admin panel client-side) |
| /#/admin/users | Angular SPA shell |
| /#/admin/feedback | Angular SPA shell |

### 📁 FTP Directory Contents (public, 200 OK)
| File | Size | Notes |
|------|------|-------|
| quarantine/ | dir | Subdirectory with malware .url files |
| acquisitions.md | 909 B | Confidential plans |
| announcement_encrypted.md | 369 KB | Encrypted announcement |
| coupons_2013.md.bak | 131 B | Backup file |
| eastere.gg | 324 B | Easter egg |
| encrypt.pyc | 573 B | Python compiled |
| incident-support.kdbx | 3,246 B | KeePass DB |
| legal.md | 3,047 B | Legal info |
| package-lock.json.bak | 750 KB | Package lock backup |
| package.json.bak | 4,263 B | Package JSON backup |
| suspicious_errors.yml | 723 B | Error config |

## v1 API Endpoints (from spider, discovered paths)
| Method | Endpoint |
|--------|----------|
| GET | /api/v1/ |
| GET | /api/v1/products |
| GET | /api/v1/user/signup |
| GET | /api/v1/user |
| GET | /api/v1/user/1 |
| GET | /api/v1/user/current |
| GET | /api/v1/basket |
| GET | /api/v1/order |
| GET | /api/v1/administration |
| GET | /api/v1/auth |
| GET | /api/v1/auth/ |
| GET | /api/v1/security-question |
| GET | /api/v1/users |

## REST API Root Endpoints (from spider)
| Method | Endpoint |
|--------|----------|
| GET | /rest |
| GET | /rest/user |

## Key Findings
1. **Error Disclosure:** 500 errors expose full Express stack traces with file paths (`/juice-shop/build/routes/angular.js:18:18`)
2. **CORS Wildcard:** All responses include `Access-Control-Allow-Origin: *`
3. **Missing CSP:** No Content-Security-Policy header on most endpoints
4. **Auth via Bearer token:** Endpoints check for `Authorization: Bearer <token>` header
5. **SPA Architecture:** All hash routes serve the same Angular shell (client-side routing)
6. **FTP exposure:** Backup files (.bak), compiled Python (.pyc), KeePass DB (.kdbx) publicly accessible