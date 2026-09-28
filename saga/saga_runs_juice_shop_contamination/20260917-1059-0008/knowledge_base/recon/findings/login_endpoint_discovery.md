# Login Endpoint Discovery

## Working Endpoint
- **POST `/rest/user/login`** — Returns HTTP 200 with JWT Bearer token

### Request Format
```json
{
  "email": "test@example.com",
  "password": "Test1234!"
}
```

### Response Format
```json
{
  "authentication": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "bid": 6,
    "umail": "test@example.com"
  }
}
```

### Authentication Mechanism
- JWT Bearer token returned in `authentication.token` field
- Token should be sent in `Authorization: Bearer <token>` header for authenticated requests
- ZAP credentials registered for automated authenticated scanning

## Failed Endpoints (returned 500 or non-API response)
| Endpoint | Method | Result |
|----------|--------|--------|
| `/api/authenticate` | POST | 500 - Unexpected path |
| `/api/users/login` | POST | 500 - Unexpected path |
| `/api/auth/login` | POST | 500 - Unexpected path |
| `/user/login` | POST | 200 - Returns HTML SPA page (not API) |

## API Discovery Endpoints (all returned 500)
| Endpoint | Method | Result |
|----------|--------|--------|
| `/api/` | GET | 500 - Unexpected path |
| `/api/v1/` | GET | 500 - Unexpected path |
| `/api/rest/` | GET | 500 - Unexpected path |
| `/api/feedback` | GET | 500 - Unexpected path |

## ZAP Configuration
- **Login URL**: `http://juiceshop.local:3000/rest/user/login`
- **Username field**: `email`
- **Password field**: `password`
- **ZAP user_id**: 290
- **Context ID**: 1
- **Logged in indicator**: `Log out`
- **Logged out indicator**: `Sign in`