# Hackergram Attack Surface

## Application Overview
- **Type:** Social media / messaging web application
- **Backend:** Python 3.8.10 / Flask (Werkzeug/3.0.6)
- **Frontend:** Bootstrap v4.0.0, jQuery 3.6.4
- **Authentication:** Form-based (session cookie, HttpOnly)
- **Session:** `session` cookie containing base64-encoded username (e.g., `{"username":"mr_robot"}`)

## Discovered Endpoints & Input Parameters

### Unauthenticated Endpoints
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|------------------|-------|
| `/` | GET | — | Homepage / feed (redirects to authenticated view) |
| `/login` | GET | — | Login page |
| `/login` | POST | `username`, `password` | Authentication form |
| `/signup` | GET | — | Registration page |
| `/signup` | POST | `username`, `password`, `name` | Registration form |
| `/sitemap.xml` | GET | — | Site map |
| `/robots.txt` | GET | — | Returns 404 |

### Authenticated — Profile & Users
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|------------------|-------|
| `/profile` | GET | `username` (query) | View any user's profile; user-controllable in HTML attributes (potential XSS) |
| `/users` | GET | `search` (query) | Search users by username |
| `/profile?username=admin` | GET | `username=admin` | Admin user profile visible |

### Authenticated — Posts
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|------------------|-------|
| `/create_post` | GET | `content` (query) | New post page; pre-fills content from query param |
| `/create_post` | POST | `content` (form field) | Create a new post |
| `/edit_post` | GET | `id` (query) | Edit existing post by ID |
| `/delete_post` | GET | `id` (query) | Delete post by ID |
| `/posts` | GET | — | Search posts; **returns HTTP 500** (internal server error) |

### Authenticated — Messaging
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|------------------|-------|
| `/messages` | GET | `search` (query) | Search messages by content |
| `/direct_messages` | GET | `username` (query) | View DMs with a specific user |
| `/direct_messages` | POST | `username` (form) | Send a direct message |

### Authenticated — Friends & Social
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|------------------|-------|
| `/friends` | GET | `username`, `search` (query) | View/search friends list |
| `/request_friend` | POST | `username` (hidden form field) | Send friend request |
| `/remove_friend` | POST | `username` (hidden form field) | Remove a friend |
| `/requests` | GET | `username`, `origin` (query) | View friendship requests |
| `/requests` | POST | `username`, `origin` (hidden form fields) | Accept/decline friendship requests |
| `/remove_request` | POST | `username`, `origin` (hidden form fields) | Remove a friend request |

### Authenticated — Account
| Endpoint | Method | Input Parameters | Notes |
|----------|--------|------------------|-------|
| `/settings` | GET | — | Account settings page |
| `/settings` | POST | `name`, `bio`, `photo` (file upload), `photo_url`, `currentpassword`, `newpassword` | Update profile; multipart form-data; **no CSRF token** |
| `/logout` | GET | — | Logout |

### Static Assets
| Path | Method | Notes |
|------|--------|-------|
| `/static/css/main.css` | GET | |
| `/static/css/bootstrap.min.css` | GET | |
| `/static/js/jquery-3.6.4.min.js` | GET | |
| `/static/js/bootstrap.min.js` | GET | Bootstrap v4.0.0 (known vulnerable) |
| `/static/photos/*.jpg` | GET | Profile photos |
| `/static/photos/*.png` | GET | Profile photos |

## Input Points Summary (Flat Checklist)

### Query Parameters
- `username` — used in `/profile`, `/friends`, `/direct_messages`, `/requests`
- `search` — used in `/users`, `/messages`, `/friends`
- `id` — used in `/edit_post`, `/delete_post`
- `content` — used in `/create_post` (pre-fill)
- `origin` — used in `/requests` (hidden form value passed via GET)

### Form Fields (POST)
- `/login`: `username`, `password`
- `/signup`: `username`, `password`, `name` (and likely `email`)
- `/create_post`: `content`
- `/settings`: `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword`
- `/request_friend`: `username`
- `/remove_friend`: `username`
- `/requests` (accept): `username`, `origin`
- `/remove_request`: `username`, `origin`
- `/direct_messages` (send): `username`, `message` (inferred)

### Headers / Cookies
- `session` cookie (HttpOnly, contains base64-encoded username JSON)
- No CSRF tokens on any form
- No Content-Security-Policy header
- No X-Frame-Options header
- No X-Content-Type-Options header

### File Upload
- `/settings` accepts `photo` as multipart file upload

## Security Observations (for DAST)
- **No CSRF tokens** on any form — potential CSRF vulnerability
- **Server version disclosure** via `Server: Werkzeug/3.0.6 Python/3.8.10`
- **Missing security headers**: CSP, X-Frame-Options, X-Content-Type-Options
- **Vulnerable JS library**: Bootstrap v4.0.0
- **Application error disclosure**: `/posts` returns 500 with generic message
- **User-controllable HTML attribute**: `username` reflected in profile pages (potential XSS)
- **Session cookie** contains username in readable base64 format
- **No SameSite attribute** on session cookie