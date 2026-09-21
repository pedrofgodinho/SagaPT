# Hackergram Attack Surface

## Application Overview
- **Name**: Hackergram
- **Tech Stack**: Python 3.8.10, Werkzeug/3.0.6 (Flask), Bootstrap 4.0.0, jQuery 3.6.4
- **Session**: Cookie-based (`session`, HttpOnly), no SameSite attribute
- **Authentication**: Form-based login, no CSRF tokens on any form
- **Security Headers Missing**: X-Frame-Options, CSP, X-Content-Type-Options

## Discovered Endpoints and Input Points

### Unauthenticated Endpoints
| Method | URL | Inputs | Auth Required |
|--------|-----|--------|---------------|
| GET | `/` | — | No (redirects to /login) |
| GET | `/login` | — | No |
| POST | `/login` | `username` (text), `password` (password) | No |
| GET | `/signup` | — | No (redirects if already logged in) |
| GET | `/robots.txt` | — | No |
| GET | `/sitemap.xml` | — | No |
| GET | `/static/*` | — | No (CSS, JS, images) |

### Authenticated Endpoints
| Method | URL | Inputs | Auth Required |
|--------|-----|--------|---------------|
| GET | `/profile?username={username}` | `username` (query param) | Yes |
| GET | `/friends?username={username}` | `username` (query param) | Yes |
| GET | `/friends?username={username}&search={search}` | `username`, `search` (query params) | Yes |
| GET | `/messages` | — | Yes |
| GET | `/messages?search={search}` | `search` (query param) | Yes |
| GET | `/settings` | — | Yes |
| POST | `/settings` | `name` (text), `bio` (textarea), `photo` (file upload), `photo_url` (text), `currentpassword` (password), `newpassword` (password) | Yes |
| GET | `/create_post` | `content` (query param, pre-fills textarea) | Yes |
| POST | `/create_post` | `content` (textarea) | Yes |
| GET | `/edit_post?id={id}` | `id` (query param) | Yes |
| POST | `/edit_post` | `id`, `content` (presumably) | Yes |
| GET | `/delete_post?id={id}` | `id` (query param) | Yes |
| GET | `/requests` | — | Yes |
| GET | `/requests?origin={origin}&username={username}` | `origin`, `username` (query params) | Yes |
| POST | `/request_friend` | `username` (hidden field) | Yes |
| POST | `/remove_friend` | `username` (hidden field) | Yes |
| POST | `/remove_request` | `username` (hidden field) | Yes |
| GET | `/direct_messages` | — | Yes |
| GET | `/direct_messages?username={username}` | `username` (query param) | Yes |
| POST | `/direct_messages` | `username` (hidden), `message` (textarea) | Yes |
| GET | `/users` | — | Yes |
| GET | `/users?search={search}` | `search` (query param) | Yes |
| GET | `/posts` | — | Yes (returns 500 error) |
| GET | `/logout` | — | Yes |

## Complete Input Point Checklist

### Query Parameters
- [ ] `username` — used in `/profile`, `/friends`, `/direct_messages`, `/requests`, `/users`
- [ ] `search` — used in `/friends`, `/messages`, `/users`
- [ ] `origin` — used in `/requests`
- [ ] `id` — used in `/edit_post`, `/delete_post`
- [ ] `content` — used in `/create_post` (GET pre-fill)

### Form Fields (GET forms)
- [ ] `search` — friends search, messages search, users search
- [ ] `username` + `search` — combined friends search

### Form Fields (POST forms)
- [ ] `username`, `password` — login form
- [ ] `content` — create post form
- [ ] `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword` — settings form
- [ ] `username`, `message` — direct message send form
- [ ] `username` — request_friend, remove_friend, remove_request (hidden fields)

### File Uploads
- [ ] `photo` field in `/settings` POST (multipart/form-data)

### Identified Usernames
- `mr_robot` (current authenticated user)
- `admin`
- `stark`, `rick`, `satoshi`, `heisenberg`, `dpr`
- `anon1`, `anon2`, `anon3`

## Notes for DAST Agent
- **No CSRF tokens** on any form — all POST endpoints are vulnerable to CSRF
- **Session cookie** lacks SameSite attribute
- `/posts` endpoint returns 500 Internal Server Error — may indicate a bug or SQL error
- All search/query parameters are likely SQL-injection-prone (Flask/SQLite app)
- File upload in settings (`photo`) may allow path traversal or malicious file upload
- `username` parameter in URL is reflected in page content (potential XSS vector)