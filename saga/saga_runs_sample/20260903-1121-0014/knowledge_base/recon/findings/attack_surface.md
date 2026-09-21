# Attack Surface — Hackergram (http://www.hackergram.com)

## Technologies Identified
- **Framework:** Werkzeug/3.0.6 Python/3.8.10 (Flask WSGI toolkit)
- **Frontend:** Bootstrap v4.0.0, jQuery 3.6.4
- **Session:** Cookie-based session (`Set-Cookie: session`)
- **Security Headers Missing:** CSP, X-Frame-Options, X-Content-Type-Options
- **CSRF Protection:** None (no anti-CSRF tokens in any form)

## Authentication
- **Method:** Form-based authentication (HTTP POST)
- **Login Endpoint:** `POST /login`
- **Credentials Configured:** `mr_robot` / `elliot123` (ZAP user_id: 32)
- **Logged-in Indicator:** "Log out" text in navbar
- **Logged-out Indicator:** "Sign In" link in navbar

## Endpoints and Input Points

### 1. Authentication & Registration
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/login` | POST | `username`, `password` | Login form |
| `/signup` | POST | `username`, `name`, `password` | Registration form |
| `/logout` | GET | — | Logout (redirect) |

### 2. Profile & User Pages
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/` | GET | — | Homepage / feed (auth required) |
| `/profile?username=<username>` | GET | `username` (query) | View user profile |
| `/users` | GET | `search` (query) | Search users by username |
| `/users?search=<query>` | GET | `search` (query) | User search results |

### 3. Friends / Social
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/friends?username=<user>` | GET | `username` (query) | View user's friends list |
| `/friends?username=<user>&search=<query>` | GET | `username`, `search` (query) | Search within friends |
| `/friends` | GET | `username` (hidden form), `search` (query) | Friends search form |
| `/request_friend` | POST | `username` (hidden) | Send friend request |
| `/remove_friend` | POST | `username` (hidden) | Remove a friend |

### 4. Friendship Requests
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/requests` | GET | — | View incoming friend requests |
| `/requests?username=<user>&origin=requests` | GET | `username`, `origin` (query) | Accept friend request |
| `/remove_request` | POST | `username`, `origin` (hidden) | Decline friend request |

### 5. Posts / Feed
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/create_post` | GET | — | New post form page |
| `/create_post` | POST | `content` (textarea) | Create a new post |
| `/posts` | GET | — | Search posts (currently returns 500 error) |
| `/posts?search=<query>` | GET | `search` (query) | Search posts by content |
| `/edit_post?id=<id>` | GET | `id` (query) | Edit post form page |
| `/edit_post` | POST | `id` (hidden), `content` (textarea) | Save edited post |
| `/delete_post?id=<id>` | GET | `id` (query) | Delete a post |

### 6. Messaging
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/messages` | GET | — | View all messages |
| `/messages?search=<query>` | GET | `search` (query) | Search messages by content |
| `/direct_messages` | GET | — | Direct messages inbox |
| `/direct_messages?username=<user>` | GET | `username` (query) | View DM conversation with user |
| `/direct_messages` | POST | (message content + recipient) | Send direct message |

### 7. Settings / Account
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/settings` | GET | — | Settings page |
| `/settings` | POST (multipart/form-data) | `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword` | Update profile settings |

### 8. Static Assets
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/static/css/main.css` | GET | Application stylesheet |
| `/static/css/bootstrap.min.css` | GET | Bootstrap CSS |
| `/static/js/jquery-3.6.4.min.js` | GET | jQuery library |
| `/static/js/bootstrap.min.js` | GET | Bootstrap JS |
| `/static/photos/*` | GET | User photos (icon.jpg, mrrobot.png, heisenberg.png, rick.png, stark.jpg, dpr.jpg, default.jpg, etc.) |

### 9. Other
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sitemap.xml` | GET | Site map |
| `/robots.txt` | GET | Robots file |
| `/x` | GET | Not found (404) |

## Input Point Summary Checklist

### Query String Parameters (GET)
- `username` — used in `/profile`, `/friends`, `/direct_messages`, `/requests`
- `search` — used in `/users`, `/posts`, `/messages`, `/friends`
- `id` — used in `/edit_post`, `/delete_post`
- `origin` — used in `/requests` (value: "requests")

### Form Fields (POST)
| Form | Fields |
|------|--------|
| Login (`/login`) | `username`, `password` |
| Signup (`/signup`) | `username`, `name`, `password` |
| Create Post (`/create_post`) | `content` |
| Edit Post (`/edit_post`) | `id` (hidden), `content` |
| Settings (`/settings`) | `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword` |
| Request Friend | `username` (hidden) |
| Remove Friend | `username` (hidden) |
| Remove Request | `username` (hidden), `origin` (hidden) |
| Direct Messages | (message content + recipient) |

### Hidden Form Fields
- `username` — on friends search, request/accept friend forms
- `origin` — on request accept/decline forms (value: "requests")
- `id` — on edit_post, delete_post forms

### File Upload
- `photo` — multipart file upload on `/settings`

### URL Path Parameters
- None explicit (all parameters passed via query string or form)

### Headers of Interest
- `Cookie: session` — session management
- `Server: Werkzeug/3.0.6 Python/3.8.10` — version disclosure
- No CSRF tokens in any form submissions

## Notable Observations
1. **No CSRF protection** on any form — all forms lack anti-CSRF tokens
2. **Server version disclosure** — Werkzeug/Python version exposed in headers
3. **Missing security headers** — no CSP, X-Frame-Options, or X-Content-Type-Options
4. **`/posts` endpoint returns 500 Internal Server Error** — potential application bug
5. **`/settings` accepts file upload** — `photo` field is a file input
6. **`create_post` page reads `content` from URL query params** — JavaScript pre-fills textarea from `?content=` parameter
7. **Multiple user accounts discovered:** admin, mr_robot, rick, stark, satoshi, heisenberg, dpr, anon1, anon2, anon3
8. **Direct message contains reflected XSS payload** in message body: `"><script>alert(1)</script>`
