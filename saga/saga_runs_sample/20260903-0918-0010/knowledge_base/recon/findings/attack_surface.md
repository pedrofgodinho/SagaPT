# Attack Surface - Hackergram (http://www.hackergram.com)

## Authentication Status
- **Credentials registered**: username=`mr_robot`, password=`elliot123`
- **Auth method**: Form-based authentication via POST to /login
- **Session**: Cookie-based (`session` header, HttpOnly, Path=/)
- **Logged-in indicator**: "Sign Out" / "Welcome to Hackergram"
- **Logged-out indicator**: "Sign In" / "Access your Hackergram account"

## Technologies Identified
- **Backend**: Flask/Werkzeug 3.0.6 / Python 3.8.10
- **Frontend**: Bootstrap 4.0.0, jQuery 3.6.4
- **Session**: Server-side session cookies (HttpOnly)
- **No CSRF tokens** on any forms
- **No CSP header** (commented out in HTML)
- **Missing security headers**: X-Frame-Options, X-Content-Type-Options, SameSite on cookies

## Discovered Users
mr_robot, stark, rick, satoshi, heisenberg, admin, dpr, anon1, anon2, anon3, ZAP

---

## Endpoints Discovered

### Authentication Endpoints
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/login` | — | Login form page |
| POST | `/login` | `username` (text), `password` (password) | Form-based login |
| GET | `/signup` | — | Signup form page |
| POST | `/signup` | `username` (text), `name` (text), `password` (password) | User registration |
| GET | `/logout` | — | Clears session cookie |

### Profile & User Pages
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/profile?username=XXX` | `username` (query string, required) | User profile display |
| GET | `/users` | `search` (query string, GET) | Search users by username |
| GET | `/users?search=XXX` | `search` (query string) | User search results |

### Social Features (Friends)
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/friends?username=XXX` | `username` (query string) | Friend list for user |
| GET | `/friends?username=XXX&search=XXX` | `username` (hidden GET), `search` (query string) | Search friends by username |
| POST | `/request_friend` | `username` (hidden form field) | Send friend request |
| POST | `/remove_friend` | (hidden form field) | Remove friend |

### Messaging
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/messages` | `search` (query string, GET) | Search all messages |
| GET | `/messages?search=XXX` | `search` (query string) | Message search results |
| GET | `/direct_messages?username=XXX` | `username` (query string) | Direct messages with user |
| POST | `/direct_messages?username=XXX` | `username` (query string) | Send direct message form |

### Posts
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/create_post` | `content` (query string, read via JS) | Create new post page |
| POST | `/create_post` | `content` (textarea) | Submit new post |
| GET | `/edit_post?id=XXX` | `id` (query string, hidden form) | Edit post page |
| POST | `/edit_post` | (form data) | Update post |
| GET | `/delete_post?id=XXX` | `id` (query string, hidden form) | **Delete post via GET** (CSRF vulnerability) |
| GET | `/posts` | — | Posts search page (**500 Internal Server Error**) |

### Settings
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/settings` | — | User settings page |
| POST | `/settings` | `name` (text), `bio` (textarea), `photo` (file upload), `photo_url` (text), `currentpassword` (password), `newpassword` (password) | **multipart/form-data** |

### Requests (Friendship)
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/requests` | — | Friendship requests page |
| POST | `/remove_request` | (hidden form field) | Remove friend request |
| GET | `/requests?origin=requests&username=XXX` | `origin` (query string), `username` (query string) | Requests from profile |
| GET | `/requests?origin=profile&username=XXX` | `origin` (query string), `username` (query string) | Requests to profile |

### Static Assets
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/static/css/main.css` | Stylesheet |
| GET | `/static/css/bootstrap.min.css` | Bootstrap CSS |
| GET | `/static/js/jquery-3.6.4.min.js` | jQuery library |
| GET | `/static/js/bootstrap.min.js` | Bootstrap JS |
| GET | `/static/photos/icon.jpg` | Favicon |
| GET | `/static/photos/*.jpg/png` | User profile photos |

### Other
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/x` | Returns 404 |
| GET | `/robots.txt` | Returns 404 |
| GET | `/sitemap.xml` | Returns 404 |

---

## Complete Input Parameter Inventory

### Query String Parameters (GET)
| Parameter | Endpoints Affected | Type | Description |
|-----------|-------------------|------|-------------|
| `username` | `/profile`, `/friends`, `/direct_messages`, `/requests` | string | Target username |
| `id` | `/edit_post`, `/delete_post` | integer | Post ID |
| `search` | `/users`, `/messages`, `/friends`, `/posts` | string | Search query |
| `origin` | `/requests` | string | Request origin context |

### Form Fields (POST)
| Field | Forms | Type | Description |
|-------|-------|------|-------------|
| `username` | `/login`, `/signup`, `/request_friend` | text | Username |
| `password` | `/login`, `/signup` | password | Password |
| `name` | `/signup`, `/settings` | text | Display name |
| `content` | `/create_post` | textarea | Post/message content |
| `bio` | `/settings` | textarea | User bio |
| `photo` | `/settings` | file | Profile photo upload |
| `photo_url` | `/settings` | text | Profile photo URL |
| `currentpassword` | `/settings` | password | Current password verification |
| `newpassword` | `/settings` | password | New password |

### Hidden Inputs
| Field | Forms | Value Source | Description |
|-------|-------|-------------|-------------|
| `#user` value | Nav bar (all authenticated pages) | Session | Current logged-in username |
| `username` | `/request_friend` | Profile URL | Target user for friend request |
| `id` | `/edit_post`, `/delete_post` | Post ID | Post being edited/deleted |

### JavaScript-Accessible Inputs
| Parameter | Page | Description |
|-----------|------|-------------|
| `content` (query string) | `/create_post` | Pre-fills content textarea via URL parameter |

---

## Security Observations
1. **No CSRF tokens** on any form
2. **DELETE operations via GET** (`/delete_post?id=XXX`) - trivial CSRF
3. **POST operations via GET** (`/edit_post?id=XXX`) - trivial CSRF
4. **Application error disclosure** on `/posts` (500 error)
5. **Session cookie lacks SameSite attribute**
6. **No Content-Security-Policy header** (commented out in source)
7. **Server version disclosed** in `Server` header
8. **User-controllable HTML attributes** in profile URLs (potential XSS vector)
9. **Direct URL manipulation** possible on all `username` and `id` parameters