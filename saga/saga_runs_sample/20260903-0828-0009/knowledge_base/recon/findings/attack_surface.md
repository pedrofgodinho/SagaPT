# Hackergram - Attack Surface

## Application Overview
Hackergram is a social media web application (Python/Flask, Werkzeug 3.0.6). It includes user authentication, profiles, friend management, posts, messaging, and settings functionality.

## Authentication
- **POST /login** - Form-based login
  - Fields: `username` (text), `password` (password)
  - Session cookie: `session` (HttpOnly)

## Endpoints Discovered

### Navigation / Static
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage / feed |
| GET | `/login` | Login page |
| GET | `/signup` | Sign up page (redirects if logged in) |
| GET | `/logout` | Logout endpoint |
| GET | `/sitemap.xml` | Sitemap |
| GET | `/robots.txt` | Robots.txt |
| GET | `/x` | Unknown endpoint |

### Posts
| Method | Endpoint | Description | Input Parameters |
|--------|----------|-------------|------------------|
| GET | `/create_post` | Create post page | None (GET) |
| POST | `/create_post` | Submit new post | `content` (textarea) |
| GET | `/edit_post` | Edit post page | `id` (hidden field, GET param) |
| POST | `/edit_post` | Submit edited post | `content` (textarea), `id` |
| GET | `/delete_post` | Delete post | `id` (hidden field, GET param) |
| GET | `/posts` | Search posts page | `search` (query param) — **500 error observed** |

### Profiles
| Method | Endpoint | Description | Input Parameters |
|--------|----------|-------------|------------------|
| GET | `/profile` | View user profile | `username` (query param) |

### Friends / Social
| Method | Endpoint | Description | Input Parameters |
|--------|----------|-------------|------------------|
| GET | `/friends` | View/search friends | `username` (hidden field), `search` (query param) |
| POST | `/request_friend` | Send friend request | `username` (hidden field) |
| POST | `/remove_friend` | Remove friend | `username` (hidden field) |
| GET | `/requests` | View friendship requests | None (GET) |
| GET | `/requests` | View requests with origin | `origin` (query param: "profile" or "requests"), `username` (query param) |
| POST | `/remove_request` | Remove friendship request | `username` (hidden field), `origin` (hidden field) |

### Messaging
| Method | Endpoint | Description | Input Parameters |
|--------|----------|-------------|------------------|
| GET | `/messages` | Search messages page | `search` (query param) |
| GET | `/direct_messages` | Direct messages page | None (GET) |
| GET | `/direct_messages` | DM with specific user | `username` (query param) |
| POST | `/direct_messages` | Send direct message | `username` (hidden field), `message` (textarea) |

### Users
| Method | Endpoint | Description | Input Parameters |
|--------|----------|-------------|------------------|
| GET | `/users` | Search users page | `search` (query param) |

### Settings
| Method | Endpoint | Description | Input Parameters |
|--------|----------|-------------|------------------|
| GET | `/settings` | Account settings page | None (GET) |
| POST | `/settings` | Update account settings | `name` (text), `bio` (textarea), `photo` (file upload), `photo_url` (text), `currentpassword` (password), `newpassword` (password) — `enctype: multipart/form-data` |

## Summary of All Input Points

### Query String Parameters (GET)
- `username` — used across /profile, /friends, /direct_messages, /requests
- `search` — used across /users, /posts, /messages, /friends
- `id` — used for /edit_post, /delete_post
- `origin` — used on /requests (values: "profile", "requests")

### Form Fields (POST)
- `/login`: `username`, `password`
- `/create_post`: `content`
- `/edit_post`: `content`, `id`
- `/direct_messages`: `username` (hidden), `message`
- `/request_friend`: `username` (hidden)
- `/remove_friend`: `username` (hidden)
- `/remove_request`: `username` (hidden), `origin` (hidden)
- `/settings`: `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword`

### File Upload
- `/settings`: `photo` field accepts file uploads (multipart/form-data)

## Notable Observations
- No Anti-CSRF tokens found on any forms
- Session cookie lacks SameSite attribute
- Server version information disclosed (Werkzeug/3.0.6 Python/3.8.10)
- CSP header not set
- X-Frame-Options header missing
- /posts endpoint returns HTTP 500 Internal Server Error
- /edit_post and /delete_post use GET requests with hidden form fields
- Settings page accepts file uploads (photo) and URL input (photo_url)
- Direct messages page shows evidence of previously stored XSS payloads (`<script>`, quotes)
- Users discovered: admin, mr_robot, rick, stark, heisenberg, satoshi, dpr, anon1, anon2, anon3