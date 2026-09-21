# Attack Surface - Hackergram

## Application Type
Social networking web application built with Python/Werkzeug. Features include user profiles, posts, friend requests, direct messaging, and user search.

## Credentials
- Username: `mr_robot`
- Password: `elliot123`
- Auth method: Form-based authentication via `/login` (POST)
- Session: Cookie-based (`session` cookie)

---

## Unauthenticated Endpoints

| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/` | GET | None | Unauthenticated homepage |
| `/login` | GET | None | Login page (renders form) |
| `/login` | POST | `username`, `password` | Authentication endpoint |
| `/signup` | GET | None | Sign-up page (renders form) |
| `/signup` | POST | `username`, `name`, `password` | User registration endpoint |

---

## Authenticated Endpoints

### Profile & User Management

| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/` | GET | None | Authenticated homepage (feed) |
| `/profile` | GET | `username` (query param) | View user profile |
| `/users` | GET | `search` (query param) | Search users by username |
| `/settings` | GET | None | Settings page (renders form) |
| `/settings` | POST | `name`, `bio`, `photo` (file upload), `photo_url`, `currentpassword`, `newpassword` | Update profile settings |
| `/logout` | GET | None | Logout endpoint |

### Posts

| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/create_post` | GET | None | New post page (renders form) |
| `/create_post` | POST | `content` (textarea) | Create a new post |
| `/edit_post` | GET | `id` (query param) | Edit post page (renders form) |
| `/edit_post` | POST | `id` (hidden), `content` (textarea) | Update a post |
| `/delete_post` | GET | `id` (query param) | Delete a post |
| `/posts` | GET | None | Search posts page (returns 500 error) |

### Friends & Requests

| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/friends` | GET | `username` (hidden/query), `search` (query param) | View/search friends list |
| `/request_friend` | POST | `username` | Send a friend request |
| `/remove_friend` | POST | `username` | Remove a friend |
| `/requests` | GET | None | View pending friend requests |
| `/remove_request` | POST | `username` (hidden), `origin` (hidden: "profile" or "requests") | Remove a friend request |

### Messaging

| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/messages` | GET | `search` (query param) | Search/view messages |
| `/direct_messages` | GET | `username` (query param) | View direct messages with a user |
| `/direct_messages` | POST | `username` (hidden), `content` (likely) | Send a direct message |

---

## Discovered Usernames
- `admin` - Administrator
- `anon1`, `anon2`, `anon3` - Anonymous users
- `dpr` - Dread Pirate Roberts
- `heisenberg`
- `mr_robot` - Current authenticated user
- `rick` - Rick Sanchez
- `satoshi` - Satoshi Nakamoto
- `stark` - Ned Stark

## Security-Relevant Observations
- No Anti-CSRF tokens on any forms (ZAP alert 10202)
- Server header leaks version: `Werkzeug/3.0.6 Python/3.8.10`
- Missing security headers: CSP, X-Content-Type-Options, X-Frame-Options
- Cookie without SameSite attribute on login response
- `/posts` endpoint returns 500 Internal Server Error (application error disclosure)
- User-controllable HTML element attribute potential XSS on profile pages
- Sensitive information exposed in URL (`username` query parameter)
- Bootstrap v4.0.0 (known vulnerable JS library)
- File upload endpoint at `/settings` (photo field)

## Static Resources
- `/static/css/main.css`, `/static/css/bootstrap.min.css`
- `/static/js/jquery-3.6.4.min.js`, `/static/js/bootstrap.min.js`
- `/static/photos/` - user profile images (icon.jpg, mrrobot.png, heisenberg.png, stark.jpg, rick.png, dpr.jpg, default.jpg)
