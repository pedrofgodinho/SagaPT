# Hackergram Attack Surface

**Application Type:** Social media / messaging platform (Python/Werkzeug backend)
**Authentication:** Form-based (login page at /login)
**Test Credentials:** username: `mr_robot`, password: `elliot123`

---

## Unauthenticated Endpoints

| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|------------------|
| `/` | GET | Homepage (redirects to login) | None |
| `/login` | GET | Login page | None |
| `/login` | POST | Login form submission | `username`, `password` |
| `/signup` | GET | Registration page | None |
| `/signup` | POST | Registration form submission | `username`, `name`, `password` |

## Authenticated Endpoints

### Profile & Users
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|------------------|
| `/profile?username=<user>` | GET | View user profile | `username` (URL param) |
| `/users` | GET | Search users page | None |
| `/users?search=<query>` | GET | Search users by username | `search` (GET param) |

### Friends Management
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|------------------|
| `/friends?username=<user>` | GET | View user's friends list | `username` (URL param) |
| `/friends?username=<user>&search=<query>` | GET | Search friends by username | `username` (hidden form), `search` (GET param) |
| `/request_friend` | POST | Send friend request | `username` (hidden form field) |
| `/remove_friend` | POST | Remove friend | `username` (hidden form field) |
| `/requests` | GET | View pending friend requests | None |
| `/requests?origin=<origin>&username=<user>` | GET | Accept/decline requests | `origin` (profile or requests), `username` |
| `/remove_request` | POST | Remove friend request | `username`, `origin` (hidden form fields) |

### Messaging
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|------------------|
| `/messages` | GET | View all messages | None |
| `/messages?search=<query>` | GET | Search messages by content | `search` (GET param) |
| `/direct_messages?username=<user>` | GET | View messages with specific user | `username` (URL param) |
| `/direct_messages` | POST | Send direct message | `username` (hidden form field), `message` (textarea) |

### Posts
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|------------------|
| `/create_post` | GET | Create new post page | None |
| `/create_post` | POST | Submit new post | `content` (textarea) |
| `/edit_post?id=<post_id>` | GET | Edit post page | `id` (URL param) |
| `/edit_post` | POST | Submit edited post | `id` (likely hidden), `content` (textarea) |
| `/delete_post?id=<post_id>` | GET | Delete post | `id` (URL param) |
| `/posts` | GET | Search/browse posts | None (may accept search params) |

### Settings
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|------------------|
| `/settings` | GET | User settings page | None |
| `/settings` | POST | Update user settings | `name` (text), `bio` (textarea), `photo` (file upload), `photo_url` (text), `currentpassword` (password), `newpassword` (password) |

### Authentication
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|------------------|
| `/logout` | GET | Logout | None |

---

## Input Points Summary

### URL Parameters (GET)
- `username` — used in `/profile`, `/friends`, `/direct_messages`
- `search` — used in `/users`, `/messages`, `/friends`
- `id` — used in `/edit_post`, `/delete_post`
- `origin` — used in `/requests` (values: `profile`, `requests`)

### Form Fields (POST)
- **Login:** `username`, `password`
- **Signup:** `username`, `name`, `password`
- **Settings:** `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword`
- **Create Post:** `content`
- **Edit Post:** `content`
- **Direct Messages:** `username` (hidden), `message`
- **Friend Management:** `username` (hidden), `origin` (hidden)

### File Upload
- `/settings` accepts `photo` file upload (multipart/form-data)

### Search Functionality
- Search users: `/users?search=<query>`
- Search messages: `/messages?search=<query>`
- Search friends: `/friends?username=<user>&search=<query>`

---

## Notable Observations
- **No CSRF tokens** on any forms (flagged by ZAP)
- **Server header leaks** Werkzeug/3.0.6 Python/3.8.10
- **Missing security headers**: CSP, X-Frame-Options, X-Content-Type-Options
- **Admin user exists**: `admin` (accessible via `/profile?username=admin`)
- **Multiple users discovered**: mr_robot, admin, satoshi, dpr, heisenberg, stark, rick, ZAP, anon1, anon2, anon3
- **Application error disclosure** on `/posts` (500 Internal Server Error with debug info)
- **Potential XSS** in username parameter (ZAP flagged user-controllable HTML attribute)

---

## Static Resources
- `/static/css/main.css`
- `/static/css/bootstrap.min.css`
- `/static/js/jquery-3.6.4.min.js`
- `/static/js/bootstrap.min.js`
- `/static/photos/` — contains user photos (icon.jpg, mrrobot.png, heisenberg.png, dpr.jpg, stark.jpg, rick.png, default.jpg)