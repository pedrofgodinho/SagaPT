# Hackergram Attack Surface Map

**Application:** Hackergram — Python/Werkzeug social media platform (Bootstrap 4.0.0, jQuery 3.6.4)
**Authentication:** Form-based at `/login` (username/password). Session in HttpOnly cookie.
**Test Credentials:** `mr_robot` / `elliot123`
**Tech Stack:** Werkzeug/3.0.6 Python/3.8.10, Bootstrap v4.0.0, jQuery 3.6.4

---

## Endpoints & Input Parameters

### Authentication
| Endpoint | Method | Input Parameters |
|----------|--------|-----------------|
| `/login` | GET | — |
| `/login` | POST | `username`, `password` |
| `/signup` | GET | — |
| `/signup` | POST | `username`, `password`, `email` (registration form) |
| `/logout` | GET | — |

### Posts
| Endpoint | Method | Input Parameters |
|----------|--------|-----------------|
| `/create_post` | GET | `?content` (query param pre-fills textarea) |
| `/create_post` | POST | `content` (textarea) |
| `/edit_post` | GET | `?id` (hidden in form, also URL param) |
| `/edit_post` | POST | `id` (hidden), `content` (textarea) |
| `/delete_post` | GET | `?id` |
| `/posts` | GET | `?search` (returns 500 error — application bug) |

### Profile & Users
| Endpoint | Method | Input Parameters |
|----------|--------|-----------------|
| `/profile` | GET | `?username` |
| `/users` | GET | `?search` |

### Settings (Profile Editing)
| Endpoint | Method | Input Parameters |
|----------|--------|-----------------|
| `/settings` | GET | — |
| `/settings` | POST | `name`, `bio`, `photo` (file upload, multipart), `photo_url`, `currentpassword`, `newpassword` |

### Friends / Social
| Endpoint | Method | Input Parameters |
|----------|--------|-----------------|
| `/friends` | GET | `?username`, `?search` |
| `/request_friend` | POST | `username` |
| `/remove_friend` | POST | `username` |
| `/requests` | GET | — |
| `/requests` (via profile links) | POST | `username`, `origin` (hidden: `profile` or `requests`) |
| `/remove_request` | POST | `username` |

### Messaging
| Endpoint | Method | Input Parameters |
|----------|--------|-----------------|
| `/messages` | GET | `?search` |
| `/direct_messages` | GET | `?username` |
| `/direct_messages` | POST | `username`, message body (textarea for sending DMs) |

### Static / Other
| Endpoint | Method | Input Parameters |
|----------|--------|-----------------|
| `/` (homepage) | GET | — |
| `/sitemap.xml` | GET | — |
| `/robots.txt` | GET | — |
| `/static/*` | GET | — |
| `/x` | GET | — (discovered in spider, purpose unknown) |

---

## Summary of Input Points

1. **Query Parameters:**
   - `username` — on `/profile`, `/friends`, `/direct_messages`
   - `search` — on `/users`, `/posts`, `/messages`, `/friends`
   - `id` — on `/edit_post`, `/delete_post`
   - `content` — on `/create_post` (pre-fill)
   - `origin` — on `/requests` (POST hidden field, values: `profile` or `requests`)

2. **Form POST Fields:**
   - Login: `username`, `password`
   - Signup: `username`, `password`, `email`
   - Create/Edit Post: `content`, `id` (hidden)
   - Settings: `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword`
   - Friends: `username` (hidden), `origin` (hidden)
   - Direct Messages: `username`, message body

3. **File Upload:**
   - `/settings` POST accepts `photo` file upload (multipart/form-data)

4. **Hidden/Pre-filled Inputs:**
   - `#user` div on every page: `<div type="hidden" id="user" value="mr_robot">`
   - `id` hidden fields on edit/delete post forms
   - `origin` hidden field on remove_request form

## Security Observations (Recon Only)
- All forms lack Anti-CSRF tokens (ZAP alert 10202)
- Missing security headers: X-Frame-Options, X-Content-Type-Options, CSP
- Server version information leaked (Werkzeug/3.0.6 Python/3.8.10)
- Bootstrap v4.0.0 known vulnerable library
- `/posts?search=` endpoint returns 500 Internal Server Error
- `/direct_messages?username=stark` already reflects `<script>alert(1)</script>` — stored XSS confirmed in messages
- Session cookie lacks SameSite attribute
- User-controllable HTML attributes detected on profile pages (ZAP alert 10031)