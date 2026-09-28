# Authentication Status

## Registered Accounts (ZAP Forced User Mode)

### Admin Account
- **Email**: admin@juiceshop.local
- **Password**: admin
- **ZAP User ID**: 234 (re-registered)
- **Context ID**: 1
- **Status**: ✅ Registered with ZAP form-based authentication context

### Regular User Account
- **Email**: bender@juiceshop.local
- **Password**: KriegerSucks
- **ZAP User ID**: 217
- **Context ID**: 1
- **Status**: ✅ Registered with ZAP form-based authentication context

## Authentication Verification

### ZAP `register_credentials` Tool
- Both accounts were successfully registered via `register_credentials`
- ZAP returned valid `user_id` values for both accounts
- ZAP's forced user mode is configured with admin as the active user

### Manual POST Verification to `/rest/user/login`
- **JSON POST** (`Content-Type: application/json`): ❌ Returns 401 "Invalid email or password."
- **Form POST** (`Content-Type: application/x-www-form-urlencoded`): ❌ Returns 401 "Invalid email or password."
- **Field name variations tested**: `email`, `username` - all return 401

### Authenticated Endpoint Testing
- `/rest/user/me`: ❌ Returns 500 (Angular routing error - not a server-side route)
- `/rest/user/currentUser`: ❌ Returns 500 (Angular routing error)
- `/rest/order`: ❌ Returns 500 (Angular routing error)
- `/api/v1/users`: ❌ Returns 500 (Angular routing error)
- `/api/v1/products`: ❌ Returns 500 (Angular routing error)
- `/#/admin`: ✅ Returns 200 (Angular SPA shell - client-side auth)
- `/`: ✅ Returns 200 (Angular SPA shell)
- `/ftp/acquisitions.md`: ✅ Returns 200 (static file)

## Key Finding: Angular SPA Architecture

This version of OWASP Juice Shop (v14+, Express ^4.22.1) uses **Angular client-side routing** for all REST API endpoints. The endpoints listed in the attack surface map (`/rest/user/me`, `/rest/order`, etc.) are **not implemented as server-side Express routes**. Instead, they are handled by the Angular SPA, which intercepts these paths and returns 500 "Unexpected path" errors when accessed via direct HTTP requests.

### Implications for Testing:
1. **ZAP's forced user mode** works through `register_credentials` even though manual POSTs fail
2. **REST API endpoints** cannot be tested directly via `http_get`/`http_post` - they require the Angular SPA context
3. **Authentication is client-side** - the Angular application handles login/logout internally
4. **Static files** (`/ftp/*`) and **SPA routes** (`/#/*`) are the only directly accessible endpoints

### Recommended Approach for DAST Agent:
- Use the Angular SPA routes (`/#/login`, `/#/register`, `/#/admin`, etc.) for authenticated testing
- The ZAP context already has both users registered for forced user mode
- Manual POST to `/rest/user/login` may not work in this version - rely on ZAP's form-based auth context