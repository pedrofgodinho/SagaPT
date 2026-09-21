# Hackergram Attack Surface

## Application Overview
- **Type**: Social media / messaging web application
- **Stack**: Python/Flask (Werkzeug 3.0.6), Bootstrap 4.0.0, jQuery 3.6.4
- **Authentication**: Form-based (session cookies, HttpOnly)
- **Known users**: mr_robot, admin, stark, rick, satoshi, heisenberg, dpr, anon1, anon2, anon3

---

## Endpoints and Input Parameters

### 1. Authentication
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/login` | POST | `username`, `password` | Form fields |
| `/signup` | GET | (page exists, registration form expected) | N/A |
| `/logout` | GET | None | N/A |

### 2. User Profiles
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/profile?username=X` | GET | `username` (query string) | Query param |

### 3. Posts
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/create_post` | GET | (page with form) | N/A |
| `/create_post` | POST | `content` (textarea) | Form field |
| `/edit_post?id=X` | GET | `id` (query string) | Query param |
| `/edit_post` | POST | `id` (hidden), `content` (textarea) | Form fields |
| `/delete_post?id=X` | GET | `id` (query string) | Query param |
| `/posts` | GET | None (returns 500 error) | N/A |

### 4. Friends
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/friends?username=X` | GET | `username` (query string) | Query param |
| `/friends` | GET | `search` (text input), `username` (hidden) | Form fields (GET) |
| `/remove_friend` | POST | `username` (hidden) | Form field |

### 5. Friendship Requests
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/requests` | GET | None | N/A |
| `/requests?origin=X&username=Y` | GET | `origin`, `username` (query strings) | Query params |
| `/request_friend` | POST | `username` (hidden) | Form field |
| `/remove_request` | POST | `username` (hidden), `origin` (hidden) | Form fields |

### 6. Messages
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/messages` | GET | `search` (text input) | Form field (GET) |
| `/direct_messages` | POST | `username` (hidden), `message` (textarea) | Form fields |
| `/direct_messages?username=X` | GET | `username` (query string) | Query param |

### 7. Users Search
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/users` | GET | `search` (text input) | Form field (GET) |
| `/users?search=X` | GET | `search` (query string) | Query param |

### 8. Settings
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/settings` | POST (multipart/form-data) | `name` (text), `bio` (textarea), `photo` (file upload), `photo_url` (text), `currentpassword` (password), `newpassword` (password) | Form fields |

### 9. Other
| Endpoint | Method | Input Parameters | Type |
|----------|--------|-----------------|------|
| `/x` | GET | None | N/A (returns 404) |
| `/sitemap.xml` | GET | None | N/A |
| `/robots.txt` | GET | None | N/A |

---

## Summary of All Input Points

### Query String Parameters
- `username` — used in `/profile`, `/friends`, `/direct_messages`, `/requests`
- `search` — used in `/users`, `/messages`, `/friends`
- `id` — used in `/edit_post`, `/delete_post`
- `origin` — used in `/requests`

### Form Fields (POST)
- `username`, `password` — login form
- `content` — create_post and edit_post (textarea)
- `name` — settings (text input)
- `bio` — settings (textarea)
- `photo` — settings (file upload)
- `photo_url` — settings (text input)
- `currentpassword`, `newpassword` — settings (password inputs)
- `message` — direct_messages (textarea)
- `username` (hidden) — remove_friend, request_friend, remove_request forms
- `origin` (hidden) — remove_request form

### Form Fields (GET)
- `search` — friends, messages, users search forms
- `username` (hidden) — friends search form

### File Upload
- `photo` field in `/settings` (multipart/form-data)

---

## Notes for DAST Testing
- **No CSRF tokens** present on any form (confirmed by ZAP alerts)
- **XSS potential** in: `username` (URL parameter, profile pages), `content` (post content), `message` (direct messages), `search` (search forms), `name`, `bio`, `photo_url` (settings)
- **IDOR potential** in: `id` parameter (edit_post, delete_post), `username` parameter (profile, friends, direct_messages)
- **File upload** at `/settings` with `photo` field
- **Error disclosure**: `/posts` returns 500 Internal Server Error with debug message
- **Session cookie**: `session` set with HttpOnly but no SameSite attribute