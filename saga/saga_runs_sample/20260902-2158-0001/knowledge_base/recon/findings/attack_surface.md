# Hackergram Attack Surface

## Technology Stack
- **Backend:** Python 3.8.10 / Werkzeug 3.0.6 (Flask-like WSGI server)
- **Frontend:** Bootstrap v4.0.0, jQuery 3.6.4
- **Authentication:** Form-based (session cookies, HttpOnly, no SameSite)
- **Session:** Base64-encoded session cookie (`session`)

## Discovered Endpoints

### Public (Unauthenticated)
| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Homepage (redirects to login when unauthenticated) |
| `/login` | GET | Login page |
| `/login` | POST | Login submission |
| `/signup` | GET | Signup page |
| `/signup` | POST | Signup submission |

### Authenticated
| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Homepage / Feed (displays posts from all users) |
| `/create_post` | GET | New post page |
| `/create_post` | POST | Create post submission |
| `/edit_post` | GET | Edit post page |
| `/edit_post` | POST | Edit post submission |
| `/delete_post` | GET | Delete post |
| `/profile` | GET | User profile page |
| `/friends` | GET | Friends list page |
| `/friends` | POST | (via profile forms) |
| `/request_friend` | POST | Send friend request |
| `/remove_friend` | POST | Remove friend |
| `/requests` | GET | Friendship requests page |
| `/remove_request` | POST | Remove friendship request |
| `/messages` | GET | Messages / Search messages |
| `/direct_messages` | GET | Direct messages page |
| `/direct_messages` | POST | Send direct message |
| `/users` | GET | User search page |
| `/posts` | GET | Posts search (returns 500 error) |
| `/settings` | GET | Account settings page |
| `/settings` | POST | Update settings (multipart) |
| `/logout` | GET | Logout (resets session) |

## Input Points

### Query String Parameters
| Parameter | Endpoints | Description |
|---|---|---|
| `username` | `/profile`, `/friends`, `/direct_messages`, `/requests` | Target user for profile viewing, friends, DMs, requests |
| `search` | `/users`, `/posts`, `/messages`, `/friends` | Search query for users, posts, messages, friends |
| `id` | `/edit_post`, `/delete_post` | Post ID for edit/delete operations |
| `origin` | `/requests` | Request origin context (`profile` or `requests`) |

### POST Form Fields
| Form | Fields | Endpoint |
|---|---|---|
| Login | `username`, `password` | `/login` |
| Signup | `username`, `name`, `password` | `/signup` |
| Create Post | `content` | `/create_post` |
| Edit Post | `id`, `content` | `/edit_post` |
| Request Friend | `username` | `/request_friend` |
| Remove Friend | `username` | `/remove_friend` |
| Remove Request | `username` | `/remove_request` |
| Send DM | `content`, `to` (implied) | `/direct_messages` |
| Settings (multipart) | `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword` | `/settings` |

### GET Form Fields
| Form | Fields | Endpoint |
|---|---|---|
| Search Users | `search` | `/users` |
| Search Posts | `search` | `/posts` |
| Search Messages | `search` | `/messages` |
| Search Friends | `username`, `search` | `/friends` |

### Hidden Form Fields
| Field | Value Source | Used In |
|---|---|---|
| `username` | URL param or logged-in user | `/request_friend`, `/remove_friend`, `/remove_request` |
| `id` | URL param | `/edit_post`, `/delete_post` |

## Security Observations (from ZAP passive scan)
- **Missing CSP header** (Medium risk)
- **Missing X-Frame-Options** (Medium risk)
- **Missing X-Content-Type-Options** (Low risk)
- **Cookie without SameSite attribute** (Low risk)
- **Absence of Anti-CSRF tokens** on all forms (Medium risk)
- **Server version disclosure** via `Server` header: `Werkzeug/3.0.6 Python/3.8.10`
- **Vulnerable JS library**: Bootstrap v4.0.0
- **Application error disclosure**: `/posts` returns 500 with generic message
- **User-controllable HTML attributes** (potential XSS via `username` param)
- **Session cookie** is HttpOnly but not SameSite-restricted

## User Accounts Discovered
- `mr_robot` (current authenticated user)
- `admin` (Administrator)
- `heisenberg`
- `stark`
- `rick`
- `satoshi`
- `dpr`
- `anon1`, `anon2`, `anon3`

## Static Resources
- `/static/css/bootstrap.min.css`
- `/static/css/main.css`
- `/static/js/jquery-3.6.4.min.js`
- `/static/js/bootstrap.min.js`
- `/static/photos/icon.jpg`, `default.jpg`, `mrrobot.png`, `heisenberg.png`, `rick.png`, `stark.jpg`, `dpr.jpg`