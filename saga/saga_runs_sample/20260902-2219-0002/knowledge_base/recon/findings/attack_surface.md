# Hackergram - Attack Surface

## Application Overview
Hackergram is a social media web application built with Python/Flask (Werkzeug 3.0.6). It features user profiles, post creation/editing/deletion, direct messaging, friend requests, and search functionality.

## Authentication
- **Credentials**: username: `mr_robot`, password: `elliot123`
- **Auth method**: Form-based authentication (session cookies)
- **Session cookie**: `session` (HttpOnly, no SameSite attribute)

## Endpoints Discovered

### Authentication & User Management
| Method | Endpoint | Input Parameters | Description |
|--------|----------|-----------------|-------------|
| GET | `/login` | None | Login page |
| POST | `/login` | `username`, `password` | Login submission |
| GET | `/signup` | None | Signup page |
| GET | `/logout` | None | Logout |

### Profile & User Browsing
| Method | Endpoint | Input Parameters | Description |
|--------|----------|-----------------|-------------|
| GET | `/profile` | `username` (query) | View user profile page |
| GET | `/users` | `search` (query) | Search users by username |

### Posts
| Method | Endpoint | Input Parameters | Description |
|--------|----------|-----------------|-------------|
| GET | `/create_post` | `content` (query), None (form) | Create post page; form POST: `content` |
| POST | `/create_post` | `content` (form) | Create new post |
| GET | `/edit_post` | `id` (query) | Edit post page |
| POST | `/edit_post` | `id`, `content` (form) | Update post |
| GET | `/delete_post` | `id` (query) | Delete post |
| GET | `/posts` | `search` (query) | Search posts (returns 500 error) |

### Friends & Social
| Method | Endpoint | Input Parameters | Description |
|--------|----------|-----------------|-------------|
| GET | `/friends` | `username`, `search` (query) | Friends list with search |
| POST | `/remove_friend` | `username` (form) | Remove a friend |
| POST | `/request_friend` | `username` (form) | Send friend request |
| GET | `/requests` | None | View friendship requests |
| POST | `/remove_request` | `username`, `origin` (form) | Remove a friend request |

### Messaging
| Method | Endpoint | Input Parameters | Description |
|--------|----------|-----------------|-------------|
| GET | `/messages` | `search` (query) | Search messages by content |
| GET | `/direct_messages` | None | Direct messages inbox |
| GET | `/direct_messages` | `username` (query) | Messages with specific user |
| POST | `/direct_messages` | `username`, `message` (form) | Send direct message |

### Settings
| Method | Endpoint | Input Parameters | Description |
|--------|----------|-----------------|-------------|
| GET | `/settings` | None | User settings page |
| POST | `/settings` | `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword` | Update profile settings (multipart) |

### Static Files
| Path | Description |
|------|-------------|
| `/static/css/bootstrap.min.css` | Bootstrap CSS |
| `/static/css/main.css` | Application CSS |
| `/static/js/jquery-3.6.4.min.js` | jQuery library |
| `/static/js/bootstrap.min.js` | Bootstrap JS |
| `/static/photos/*` | User profile photos |
| `/static/photos/icon.jpg` | Site icon |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sitemap.xml` | XML sitemap |
| GET | `/robots.txt` | Robots.txt |

## Input Points Summary (All Parameters)
- **Query parameters**: `username`, `search`, `id`, `content`, `origin`
- **Form fields**: `username`, `password`, `name`, `bio`, `photo` (file upload), `photo_url`, `currentpassword`, `newpassword`, `content`, `id`, `message`
- **File uploads**: `photo` (on /settings POST)

## Security Observations from ZAP Scanning
- Missing security headers: X-Frame-Options, X-Content-Type-Options, CSP
- Session cookie lacks SameSite attribute
- No Anti-CSRF tokens on any forms
- Server version disclosure (Werkzeug/3.0.6 Python/3.8.10)
- Application error disclosure on /posts (500 error)
- Vulnerable JS library (Bootstrap v4.0.0)
- Potential XSS in user-controlled HTML attributes
- Sensitive information in URLs (username parameter)