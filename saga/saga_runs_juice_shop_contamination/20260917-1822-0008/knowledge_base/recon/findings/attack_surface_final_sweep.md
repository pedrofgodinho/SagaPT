# OWASP Juice Shop - Complete Attack Surface (Final Sweep Update)

## Application
- **Target:** http://juiceshop.local:3000
- **Type:** OWASP Juice Shop (Express ^4.22.1) - Angular SPA
- **Tech Stack:** Express.js backend, Angular frontend, Swagger UI for API docs

================================================================================
## ALL ENDPOINTS & INPUT POINTS (DAST Coverage List)
================================================================================

### Public API Endpoints (no auth required)
| # | Method | Endpoint | Input Parameters | Status | Notes |
|---|--------|----------|-----------------|--------|-------|
| 1 | GET | `/api/Products` | None (list all) | 200 | Returns all products |
| 2 | GET | `/api/Products/1` | `id` path param | 200 | Returns product JSON |
| 3 | GET | `/api/Products/2` | `id` path param | 200 | Returns product JSON |
| 4 | GET | `/api/Products` | `search` query param | 200 | ⚠️ **SQL INJECTION VULNERABLE** - `' OR '1'='1` returns all products |
| 5 | GET | `/api/Challenges` | None (list all) | 200 | Returns challenge list |
| 6 | GET | `/api/SecurityQuestions` | None (list all) | 200 | Returns security questions |
| 7 | GET | `/api/Feedbacks` | None (list all) | 200 | Returns feedback list |

### Authenticated API Endpoints (401 without auth)
| # | Method | Endpoint | Input Parameters | Status | Notes |
|---|--------|----------|-----------------|--------|-------|
| 8 | GET | `/api/Feedbacks/1` | `id` path param | 401 | Requires Authorization header |
| 9 | GET | `/api/Feedbacks/2` | `id` path param | 401 | Requires Authorization header |
| 10 | GET | `/api/Challenges/1` | `id` path param | 401 | Requires Authorization header |
| 11 | GET | `/api/SecurityQuestions/1` | `id` path param | 401 | Requires Authorization header |

### B2B API (JWT Bearer Auth Required)
| # | Method | Endpoint | Input Parameters | Status | Notes |
|---|--------|----------|-----------------|--------|-------|
| 12 | POST | `/b2b/v2/orders` | JSON body: `cid`, `orderLines[]`, `orderLinesData[]` | 401 w/o auth | JWT bearer auth required. Body params blocked by auth layer. |

### Login / Authentication Endpoints
| # | Method | Endpoint | Input Parameters | Status | Notes |
|---|--------|----------|-----------------|--------|-------|
| 13 | POST | `/rest/user/login` | Form fields: `email`, `password` | 401 | Invalid credentials → "Invalid email or password." No XSS reflection observed. |

### Swagger / OpenAPI
| # | Method | Endpoint | Input Parameters | Status | Notes |
|---|--------|----------|-----------------|--------|-------|
| 14 | GET | `/api-docs` | None | 200 | Swagger UI HTML interface |
| 15 | GET | `/api-docs/swagger-ui-init.js` | None | 200 | Embedded OpenAPI 3.0 spec for B2B API |
| 16 | GET | `/api-docs.json` | None | 500 | Error: "Unexpected path" |
| 17 | GET | `/swagger.json` | None | 200 | Returns SPA shell (not actual spec) |
| 18 | GET | `/swagger.yaml` | None | 200 | Returns SPA shell (not actual spec) |
| 19 | GET | `/openapi.json` | None | 200 | Returns SPA shell (not actual spec) |
| 20 | GET | `/openapi.yaml` | None | 200 | Returns SPA shell (not actual spec) |

### File Download Endpoints (/ftp/)
| # | Method | Endpoint | Status | Notes |
|---|--------|----------|--------|-------|
| 21 | GET | `/ftp/acquisitions.md` | 200 | Confidential acquisition plans |
| 22 | GET | `/ftp/legal.md` | 200 | Legal information |
| 23 | GET | `/ftp/announcement_encrypted.md` | 200 | Large encrypted data file |
| 24 | GET | `/ftp/incident-support.kdbx` | 200 | KeePass database binary |
| 25 | GET | `/ftp/suspicious_errors.yml` | 403 | Only .md/.pdf allowed |
| 26 | GET | `/ftp/coupons_2013.md.bak` | 403 | Only .md/.pdf allowed |
| 27 | GET | `/ftp/package.json.bak` | 403 | Only .md/.pdf allowed |
| 28 | GET | `/ftp/encrypt.pyc` | 403 | Only .md/.pdf allowed |
| 29 | GET | `/ftp/eastere.gg` | 403 | Only .md/.pdf allowed |
| 30 | GET | `/ftp/..%2f..%2f..%2fetc%2fpasswd` | 403 | Path traversal blocked |
| 31 | GET | `/ftp/../../etc/hosts` | 200 | Returns SPA shell (Angular router intercepts) |
| 32 | GET | `/ftp/../../../etc/passwd` | 200 | Returns SPA shell (Angular router intercepts) |
| 33 | GET | `/ftp/..%252f..%252f..%252fetc%252fpasswd` | 403 | Double-encoded traversal blocked |

### Security / Well-Known Files
| # | Method | Endpoint | Status | Notes |
|---|--------|----------|--------|-------|
| 34 | GET | `/.well-known/security.txt` | 200 | Contact email, PGP keys, CSAF URL, hiring link |
| 35 | GET | `/.well-known/csaf/provider-metadata.json` | 200 | CSAF metadata with 3 PGP key fingerprints |

### Angular SPA Routes (client-side routing)
| # | Method | Endpoint | Status | Notes |
|---|--------|----------|--------|-------|
| 36 | GET | `/#/about` | 200 | SPA shell |
| 37 | GET | `/#/challenges` | 200 | SPA shell |
| 38 | GET | `/#/ctf` | 200 | SPA shell |
| 39 | GET | `/#/score` | 200 | SPA shell |
| 40 | GET | `/#/leaderboard` | 200 | SPA shell |
| 41 | GET | `/#/api` | 200 | SPA shell |
| 42 | GET | `/#/data` | 200 | SPA shell |
| 43 | GET | `/#/jobs` | 200 | Referenced in security.txt, SPA shell |

### XSS Test Points
| # | Method | Endpoint | Input Parameters | Status | Notes |
|---|--------|----------|-----------------|--------|-------|
| 44 | POST | `/rest/user/login` | `email=<script>alert(1)</script>` | 401 | No XSS reflection in response |
| 45 | POST | `/rest/user/login` | `password=<script>alert(1)</script>` | 401 | No XSS reflection in response |
| 46 | GET | `/#/products` | `q=<script>alert(1)</script>` | 200 | No reflection (SPA) |
| 47 | GET | `/#/search` | `q=<script>alert(1)</script>` | 200 | No reflection (SPA) |
| 48 | GET | `/#/products` | `category=<script>alert(1)</script>` | 200 | No reflection (SPA) |

================================================================================
## INPUT POINTS SUMMARY (for DAST dispatch)
================================================================================

### Query String Parameters
- `/api/Products?search=` — **SQL INJECTION VULNERABLE** (confirmed)

### Path Parameters
- `/api/Products/{id}` — integer ID
- `/api/Feedbacks/{id}` — integer ID (auth required)
- `/api/Challenges/{id}` — integer ID (auth required)
- `/api/SecurityQuestions/{id}` — integer ID (auth required)

### Form Fields (POST /rest/user/login)
- `email` — string
- `password` — string

### JSON Body (POST /b2b/v2/orders, auth required)
- `cid` — string (customer ID)
- `orderLines[]` — array of objects with `product` and `quantity`
- `orderLinesData[]` — array (from OpenAPI spec)

================================================================================
## KEY FINDINGS SUMMARY
================================================================================

1. **SQL Injection confirmed** in `GET /api/Products?search=` — payload `' OR '1'='1` returns all products
2. **B2B API** (`POST /b2b/v2/orders`) properly requires JWT bearer auth — 401 without token
3. **Swagger spec** only available at `/api-docs` and `/api-docs/swagger-ui-init.js` — other paths return SPA shell or 500
4. **File server** restricts to .md and .pdf only; path traversal blocked by extension filter and path validation
5. **Sensitive files publicly accessible**: acquisitions.md, legal.md, encrypted announcement, KeePass DB
6. **CSAF provider metadata** with 3 PGP key fingerprints publicly available
7. **CORS misconfiguration**: `Access-Control-Allow-Origin: *` on all endpoints
8. **Missing CSP header** on all responses
9. **Angular SPA**: all routes serve same shell, no XSS reflection observed in login or SPA routes
10. **X-Recruiting header** discloses hiring page at `/#/jobs`
11. **Authentication required** for `/api/Feedbacks/{id}`, `/api/Challenges/{id}`, `/api/SecurityQuestions/{id}`
12. **Login endpoint** (`/rest/user/login`) returns generic "Invalid email or password" — no user enumeration via response difference