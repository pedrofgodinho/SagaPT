# OWASP Juice Shop Attack Surface

## Application Overview
- **Target:** http://juiceshop.local:3000
- **Application:** OWASP Juice Shop v17.x (deliberately vulnerable web application)
- **Tech Stack:** Node.js, Express ^4.22.1, Angular SPA, Material Design
- **Authentication:** Form-based (email/password), JWT tokens

## Discovered Endpoints

### Public API Endpoints (No Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/Products` | Product catalog listing |
| GET | `/api/Products/{id}` | Single product detail |
| GET | `/api/Feedbacks` | Customer feedback list |
| GET | `/api/Challenges` | Challenge metadata (20+ challenges) |
| GET | `/api/SecurityQuestions` | Security question list (14 questions) |
| GET | `/rest/web3/nftUnlocked` | Web3 NFT status |
| GET | `/rest/web3/nftMintListen` | Web3 mint endpoint |
| GET | `/` | Main SPA page |
| GET | `/robots.txt` | Disallows /ftp |
| GET | `/sitemap.xml` | Returns main page HTML |
| GET | `/ftp/` | FTP directory listing |
| GET | `/ftp/acquisitions.md` | Acquisition documents |
| GET | `/ftp/announcement_encrypted.md` | Encrypted announcement |
| GET | `/ftp/coupons_2013.md.bak` | Backup coupon file |
| GET | `/ftp/eastere.gg` | Easter egg file |
| GET | `/ftp/encrypt.pyc` | Python bytecode file |
| GET | `/ftp/incident-support.kdbx` | KeePass database |
| GET | `/ftp/legal.md` | Legal information |
| GET | `/ftp/package.json.bak` | Package backup |
| GET | `/ftp/package-lock.json.bak` | Lock file backup |
| GET | `/ftp/quarantine/` | Quarantine directory |
| GET | `/ftp/quarantine/juicy_malware_*.url` | Malware URL files |

### Authenticated API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/Users` | User registration |
| GET | `/api/Users` | User listing (requires auth) |
| GET | `/api/Feedbacks/{id}` | Individual feedback (requires auth) |
| GET | `/api/PrivacyRequests` | Privacy requests (requires auth) |
| GET | `/api/Orders` | Order history (requires auth) |

### Angular SPA Routes
| Route | Description |
|-------|-------------|
| `/#/` | Home page |
| `/#/login` | Login page |
| `/#/forgot-password` | Password reset |
| `/#/jobs` | Jobs page (referenced in X-Recruiting header) |
| `/#/recycle` | Recycling page |

### Web3 Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rest/web3/nftUnlocked` | Check NFT unlock status |
| GET | `/rest/web3/nftMintListen` | Listen for NFT mint events |
| POST | `/rest/web3/submitKey` | Submit private key |
| POST | `/rest/web3/walletNFTVerify` | Verify wallet address |
| POST | `/rest/web3/walletExploitAddress` | Wallet exploit address |

## Input Parameters

### Query String Parameters
| Parameter | Endpoint | Description |
|-----------|----------|-------------|
| `?fields=` | `/api/Products/{id}` | Field selection/filtering |
| `?limit=` | `/api/Products` | Pagination limit |
| `?order=` | `/api/Products` | Sort order |
| `?key=` | `/api/Challenges` | Challenge key filter |

### POST Form Fields (Registration)
| Field | Type | Description |
|-------|------|-------------|
| `email` | string | User email address |
| `password` | string | User password |
| `username` | string | Username |
| `name` | string | Display name |
| `securityAnswer` | string | Answer to security question |
| `securityQuestion` | integer | Security question ID (1-14) |

### Path Parameters
| Parameter | Endpoint | Description |
|-----------|----------|-------------|
| `{id}` | `/api/Products/{id}` | Product ID |
| `{id}` | `/api/Feedbacks/{id}` | Feedback ID |

### Authentication
- **Method:** JWT Bearer token in Authorization header
- **Registration:** `POST /api/Users` returns user with role, email, username
- **Test Account:** recon@test.com / ReconPass123 (registered, role: customer)

## Security Headers Observed
- `Access-Control-Allow-Origin: *` (CORS wildcard)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Feature-Policy: payment 'self'`
- `X-Recruiting: /#/jobs`
- **Missing:** Content-Security-Policy header

## Sensitive Files in FTP Directory
- `package.json.bak` - Package dependencies backup
- `package-lock.json.bak` - Lock file backup
- `coupons_2013.md.bak` - Old coupon data
- `incident-support.kdbx` - KeePass password database
- `encrypt.pyc` - Python bytecode (potential source code exposure)
- `announcement_encrypted.md` - Large encrypted file (369KB)
- `quarantine/juicy_malware_*.url` - Malware URL files
- `eastere.gg` - Easter egg file

## ZAP Alerts Identified
1. **Cross-Domain Misconfiguration** (Medium) - CORS wildcard `*`
2. **Content Security Policy Not Set** (Medium) - No CSP header
3. **Application Error Disclosure** (Low) - Stack traces exposed on 500 errors
4. **Timestamp Disclosure** (Low) - Unix timestamps in CSS/JSON
5. **Authentication Request Identified** (Info) - Login endpoints detected
6. **Modern Web Application** (Info) - Angular SPA detected

## Technology Indicators
- Express.js ^4.22.1 (from error pages)
- Angular (from `app-root` tag, chunk files)
- Node.js (runtime)
- Material Design components (from CSS)
- Font Awesome icons (from main.js)
- Cookie consent library (cookieconsent)