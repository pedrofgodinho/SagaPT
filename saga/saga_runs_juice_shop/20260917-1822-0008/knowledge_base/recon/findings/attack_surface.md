# OWASP Juice Shop - Complete Attack Surface

## Application
- **Target:** http://juiceshop.local:3000
- **Type:** OWASP Juice Shop (Express ^4.22.1) - Angular SPA
- **Tech Stack:** Express.js backend, Angular frontend, Swagger UI for API docs

## API Endpoints Discovered

### Public API Endpoints (no auth required)
| Method | Endpoint | Input Parameters | Status | Notes |
|--------|----------|-----------------|--------|-------|
| GET | `/api/Products` | None (list all) | 200 | Confirmed |
| GET | `/api/Products/1` | ID path param | 200 | Returns product JSON |
| GET | `/api/Products/2` | ID path param | 200 | Returns product JSON |
| GET | `/api/Challenges` | None (list all) | 200 | Confirmed (prior) |
| GET | `/api/SecurityQuestions` | None (list all) | 200 | Confirmed (prior) |
| GET | `/api/Feedbacks` | None (list all) | 200 | Confirmed (prior) |

### Authenticated API Endpoints (401 without auth)
| Method | Endpoint | Input Parameters | Status | Notes |
|--------|----------|-----------------|--------|-------|
| GET | `/api/Feedbacks/1` | ID path param | 401 | Requires Authorization header |
| GET | `/api/Feedbacks/2` | ID path param | 401 | Requires Authorization header |
| GET | `/api/Challenges/1` | ID path param | 401 | Requires Authorization header |
| GET | `/api/SecurityQuestions/1` | ID path param | 401 | Requires Authorization header |

### Swagger / OpenAPI
| Method | Endpoint | Input Parameters | Status | Notes |
|--------|----------|-----------------|--------|-------|
| GET | `/api-docs` | None | 200 | Swagger UI HTML |
| GET | `/api-docs/swagger-ui-init.js` | None | 200 | Embedded OpenAPI 3.0 spec for B2B API |
| GET | `/api-docs.json` | None | 500 | Error: Unexpected path |

### B2B API (from swagger-ui-init.js spec)
| Method | Endpoint | Input Parameters | Status | Notes |
|--------|----------|-----------------|--------|-------|
| POST | `/b2b/v2/orders` | JSON body: cid, orderLines, orderLinesData | Auth required | JWT bearer auth (bearerAuth) |

## File Download Endpoints (/ftp/)
| Method | Endpoint | Status | Notes |
|--------|----------|--------|-------|
| GET | `/ftp/acquisitions.md` | 200 | Confidential acquisition plans |
| GET | `/ftp/legal.md` | 200 | Legal information |
| GET | `/ftp/announcement_encrypted.md` | 200 | Large encrypted data file |
| GET | `/ftp/incident-support.kdbx` | 200 | KeePass database binary |
| GET | `/ftp/suspicious_errors.yml` | 403 | Only .md/.pdf allowed |
| GET | `/ftp/coupons_2013.md.bak` | 403 | Only .md/.pdf allowed |
| GET | `/ftp/package.json.bak` | 403 | Only .md/.pdf allowed |
| GET | `/ftp/encrypt.pyc` | 403 | Only .md/.pdf allowed |
| GET | `/ftp/eastere.gg` | 403 | Only .md/.pdf allowed |

## Security Files
| Method | Endpoint | Status | Notes |
|--------|----------|--------|-------|
| GET | `/.well-known/security.txt` | 200 | Contact, PGP keys, CSPAF metadata URL |
| GET | `/.well-known/csaf/provider-metadata.json` | 200 | CSAF metadata with 3 PGP keys |

## Angular SPA Routes (client-side routing)
| Method | Endpoint | Status | Notes |
|--------|----------|--------|-------|
| GET | `/#/about` | 200 | SPA shell |
| GET | `/#/challenges` | 200 | SPA shell |
| GET | `/#/ctf` | 200 | SPA shell |
| GET | `/#/score` | 200 | SPA shell |
| GET | `/#/leaderboard` | 200 | SPA shell |
| GET | `/#/api` | 200 | SPA shell |
| GET | `/#/data` | 200 | SPA shell |
| GET | `/#/jobs` | (referenced in security.txt) | SPA shell |

## XSS Test Results (query params on Angular routes)
| Method | Endpoint | Status | Notes |
|--------|----------|--------|-------|
| GET | `/#/products?q=<script>alert(1)</script>` | 200 | No reflection in HTML (SPA) |
| GET | `/#/search?q=<script>alert(1)</script>` | 200 | No reflection in HTML (SPA) |
| GET | `/#/products?category=<script>alert(1)</script>` | 200 | No reflection in HTML (SPA) |

## HTTP Security Headers Observed
- `X-Content-Type-Options: nosniff` ✓
- `X-Frame-Options: SAMEORIGIN` ✓
- `Access-Control-Allow-Origin: *` ⚠️ Cross-domain misconfiguration
- `Feature-Policy: payment 'self'` ✓
- `X-Recruiting: /#/jobs` (information disclosure)
- **Missing:** Content-Security-Policy (CSP) ⚠️

## Key Findings Summary
1. **OpenAPI spec embedded** in `/api-docs/swagger-ui-init.js` - B2B API with JWT auth
2. **File server restricts** to .md and .pdf only (path traversal via extension bypass possible)
3. **Sensitive files accessible**: acquisitions.md, legal.md, encrypted announcement, KeePass DB
4. **CSAF provider metadata** with PGP key fingerprints publicly available
5. **CORS misconfiguration**: `Access-Control-Allow-Origin: *` on all endpoints
6. **Missing CSP header** on all responses
7. **Angular SPA** - all routes serve same shell, XSS testing requires browser context
8. **Authentication required** for Feedbacks, Challenges, SecurityQuestions endpoints