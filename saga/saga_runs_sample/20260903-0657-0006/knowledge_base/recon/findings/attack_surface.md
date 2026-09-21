# Hackergram - Attack Surface

## Application Overview
- **Platform**: Hackergram - Social media application
- **Backend**: Python 3.8.10 / Flask (Werkzeug 3.0.6)
- **Frontend**: Bootstrap v4.0.0, jQuery 3.6.4
- **Authentication**: Form-based (session cookies, HttpOnly)
- **Known Users**: mr_robot, admin, stark, rick, satoshi, heisenberg, dpr, anon1, anon2, anon3

---

## Unauthenticated Endpoints

| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|-----------------|
| `/` | GET | Homepage (redirects to login if unauthenticated) | — |
| `/login` | GET | Login page | — |
| `/login` | POST | Login form submission | `username`, `password` (form fields) |
| `/signup` | GET | Signup page | — |
| `/signup` | POST | Signup form submission | `username`, `name`, `password` (form fields) |
| `/robots.txt` | GET | Returns 404 | — |
| `/sitemap.xml` | GET | Returns 404 | — |

---

## Authenticated Endpoints

### Profile & User Pages
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|-----------------|
| `/` | GET | Authenticated homepage (feed) | — |
| `/profile` | GET | User profile page | `username` (query parameter) |
| `/friends` | GET | User's friends list | `username` (query parameter), `search` (query param for search) |
| `/users` | GET | Search users page | `search` (query parameter) |
| `/posts` | GET | Search posts page | — (returns 500 error) |
| `/messages` | GET | Search messages page | `search` (query parameter) |

### Post Management
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|-----------------|
| `/create_post` | GET | New post form | `content` (query parameter - pre-fills textarea) |
| `/create_post` | POST | Create a new post | `content` (textarea) |
| `/edit_post` | GET | Edit post form | `id` (query parameter) |
| `/edit_post` | POST | Save edited post | `id` (hidden field), `content` (textarea) |
| `/delete_post` | GET | Delete a post | `id` (hidden field) |

### Friendship Management
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|-----------------|
| `/requests` | GET | View friendship requests | — |
| `/requests` | GET (form) | Accept friend request | `username` (hidden), `origin` (hidden) |
| `/remove_request` | POST | Decline friend request | `username` (hidden), `origin` (hidden) |
| `/request_friend` | POST | Send friend request | `username` (hidden) |

### Settings
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|-----------------|
| `/settings` | GET | User settings page | — |
| `/settings` | POST | Update user settings | `name` (text), `bio` (textarea), `photo` (file upload), `photo_url` (text), `currentpassword` (password), `newpassword` (password) |

### Logout
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|-----------------|
| `/logout` | GET | Logout (redirects to homepage) | — |

---

## Static Assets
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/static/css/main.css` | GET | Main stylesheet |
| `/static/css/bootstrap.min.css` | GET | Bootstrap CSS |
| `/static/js/jquery-3.6.4.min.js` | GET | jQuery library |
| `/static/js/bootstrap.min.js` | GET | Bootstrap JS |
| `/static/photos/icon.jpg` | GET | Site icon |
| `/static/photos/*.jpg` | GET | User profile photos |

---

## Input Points Summary (for XSS testing)

### Query Parameters (GET)
1. `username` — in `/profile?username=X`, `/friends?username=X`
2. `content` — in `/create_post?content=X`
3. `id` — in `/edit_post?id=X`, `/delete_post?id=X`
4. `search` — in `/users?search=X`, `/messages?search=X`, `/friends?search=X`

### Form Fields (POST/GET forms)
5. `username` — login form, signup form, hidden fields in requests
6. `password` — login form, signup form
7. `name` — signup form, settings form
8. `bio` — settings form
9. `photo` — settings form (file upload)
10. `photo_url` — settings form
11. `currentpassword` — settings form
12. `newpassword` — settings form
13. `content` — create_post form, edit_post form
14. `id` — edit_post hidden field, delete_post hidden field
15. `origin` — requests hidden field
16. `search` — users, messages, friends search forms

### Hidden Form Fields
17. `username` — in `/requests` accept form, `/request_friend` form
18. `origin` — in `/requests` accept/decline forms

### File Upload
19. `photo` field in `/settings` POST (enctype=multipart/form-data)

---

## Security Observations
- **No CSRF tokens** on any forms (login, signup, settings, create_post, edit_post, remove_request, request_friend)
- **Missing security headers**: CSP, X-Frame-Options, X-Content-Type-Options
- **Server version disclosure**: Werkzeug/3.0.6 Python/3.8.10
- **Cookie without SameSite** attribute on session cookie
- **500 error** on `/posts` — application error disclosure
- **Potential XSS** flagged by ZAP on `username` parameter in profile/friends pages
- **Commented-out CSP** meta tag in HTML source
- **Session cookie** is HttpOnly but not SameSite