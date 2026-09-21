# Hackergram - Attack Surface

## Application Overview
Hackergram is a social media web application built with Python/Flask (Werkzeug 3.0.6). It features user profiles, posts, direct messaging, friend requests, and user settings.

## Discovered Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/login` | Login page |
| POST | `/login` | Login form submission |
| GET | `/logout` | Logout endpoint |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/create_post` | New post creation page |
| POST | `/create_post` | Create a new post |
| GET | `/edit_post?id={id}` | Edit post page |
| POST | `/edit_post` | Submit edited post |
| GET | `/delete_post?id={id}` | Delete a post (GET-based) |
| GET | `/posts` | Posts listing (returns 500 error) |

### Profiles & Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile?username={username}` | View user profile |
| GET | `/users?search={query}` | Search users page |
| GET | `/x` | Unknown endpoint (returns 404) |

### Friends
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/friends?username={username}&search={query}` | View/search friends |
| POST | `/request_friend` | Send friend request |
| POST | `/remove_friend` | Remove friend |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/direct_messages?username={username}` | View direct messages |
| POST | `/direct_messages` | Send direct message |
| GET | `/messages?search={query}` | Search messages |

### Requests
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/requests` | View friendship requests |
| POST | `/remove_request` | Remove friendship request |

### Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/settings` | User settings page |
| POST | `/settings` | Update user settings (multipart/form-data) |

### Static Assets
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/static/css/main.css` | Main stylesheet |
| GET | `/static/css/bootstrap.min.css` | Bootstrap CSS |
| GET | `/static/js/bootstrap.min.js` | Bootstrap JS (v4.0.0) |
| GET | `/static/js/jquery-3.6.4.min.js` | jQuery 3.6.4 |
| GET | `/static/photos/*` | User profile photos |

---

## Complete Input Parameter Checklist

### Query String Parameters (GET)
- `username` — Used in: `/profile`, `/friends`, `/direct_messages`, `/users`
- `search` — Used in: `/friends`, `/messages`, `/users`
- `id` — Used in: `/edit_post`, `/delete_post`

### POST Form Body Parameters
- **Login (`/login`):** `username`, `password`
- **Create Post (`/create_post`):** `content` (also accepts via URL param)
- **Edit Post (`/edit_post`):** `id`, `content`
- **Delete Post (`/delete_post`):** `id`
- **Request Friend (`/request_friend`):** `username`
- **Remove Friend (`/remove_friend`):** `username`
- **Remove Request (`/remove_request`):** `origin`, `username`
- **Direct Messages (`/direct_messages`):** `username` (hidden), `message`
- **Settings (`/settings`):** `name`, `bio`, `photo` (file upload), `photo_url`, `currentpassword`, `newpassword`
- **Create Post page also accepts:** `content` as URL parameter (prefills textarea via JavaScript)

### File Uploads
- `photo` — POST to `/settings` (multipart/form-data)

### Hidden Form Fields
- `id` — in `/edit_post` form
- `username` — in `/direct_messages` form, `/friends` search form

### CSRF Status
- **No Anti-CSRF tokens found** on any form: `/remove_request`, `/create_post`, `/remove_friend`, `/settings`, `/edit_post`, `/direct_messages`, `/request_friend`

### Security Headers Missing
- X-Frame-Options
- Content-Security-Policy
- X-Content-Type-Options
- Cookie SameSite attribute not set

### Notable Observations
- `/posts` endpoint returns HTTP 500 Internal Server Error
- Server leaks version info: `Werkzeug/3.0.6 Python/3.8.10`
- Bootstrap v4.0.0 has known vulnerabilities
- Usernames discovered: mr_robot, admin, stark, rick, satoshi, heisenberg, dpr, anon1, anon2, anon3