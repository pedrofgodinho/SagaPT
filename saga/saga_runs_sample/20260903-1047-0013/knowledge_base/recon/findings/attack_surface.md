# Hackergram Attack Surface

## Application Overview
- **Platform**: Hackergram - Social media/messaging application
- **Backend**: Python 3.8.10 with Werkzeug/3.0.6 (Flask-based)
- **Frontend**: Bootstrap 4.0.0, jQuery 3.6.4
- **Authentication**: Form-based (session cookies, HttpOnly)
- **Security Headers Missing**: CSP, X-Frame-Options, X-Content-Type-Options, SameSite cookie attribute

## Discovered Endpoints

### Unauthenticated Endpoints
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|-----------------|
| `/` | GET | Homepage (redirects to login) | None |
| `/login` | GET | Login page | N/A |
| `/login` | POST | Login submission | `username`, `password` |
| `/signup` | GET | Registration page | N/A |
| `/signup` | POST | Registration submission | `username`, `name`, `password` |
| `/static/css/main.css` | GET | Application stylesheet | N/A |
| `/static/css/bootstrap.min.css` | GET | Bootstrap CSS | N/A |
| `/static/js/jquery-3.6.4.min.js` | GET | jQuery library | N/A |
| `/static/js/bootstrap.min.js` | GET | Bootstrap JS | N/A |
| `/static/photos/icon.jpg` | GET | Application icon | N/A |
| `/robots.txt` | GET | Returns 404 | N/A |
| `/sitemap.xml` | GET | Returns 404 | N/A |

### Authenticated Endpoints
| Endpoint | Method | Description | Input Parameters |
|----------|--------|-------------|-----------------|
| `/profile` | GET | User profile (requires `username` param) | `username` (query string) |
| `/profile?username=<user>` | GET | View specific user profile | `username` (query string) |
| `/create_post` | GET | New post creation page | N/A |
| `/create_post` | POST | Submit new post | `content` (textarea) |
| `/requests` | GET | Friendship requests page | N/A |
| `/requests` | GET | Accept friend request | `username`, `origin` (hidden fields) |
| `/requests` | POST | Decline friend request | `username`, `origin` (hidden fields) |
| `/settings` | GET | User settings page | N/A |
| `/settings` | POST | Update profile settings | `name`, `bio`, `photo` (file upload), `photo_url`, `currentpassword`, `newpassword` |
| `/users` | GET | Search users page | `search` (query string) |
| `/posts` | GET | Search posts page | `search` (query string) |
| `/messages` | GET | Search messages page | `search` (query string) |
| `/logout` | GET | Logout (clears session) | None |
| `/request_friend` | POST | Send friend request | `username` (hidden field) |
| `/remove_friend` | POST | Remove friend | `username` (hidden field) |
| `/direct_messages` | GET | Send direct message | `username` (hidden field) |
| `/friends?username=<user>` | GET | View user's friends list | `username` (query string) |

## Input Fields Summary (Potential XSS/Injection Vectors)

### Form Fields
| Field Name | Location | Type | Notes |
|-----------|----------|------|-------|
| `username` | Login form | text | Authentication input |
| `password` | Login form | password | Authentication input |
| `username` | Signup form | text | Registration input |
| `name` | Signup form | text | Display name input |
| `password` | Signup form | password | Registration input |
| `content` | Create post | textarea | Post content - **XSS risk** |
| `search` | Users search | text | User search - **XSS risk** |
| `search` | Posts search | text | Post search - **XSS risk** |
| `search` | Messages search | text | Message search - **XSS risk** |
| `name` | Settings | text | Profile name update - **XSS risk** |
| `bio` | Settings | textarea | Profile bio update - **XSS risk** |
| `photo` | Settings | file | Profile photo upload |
| `photo_url` | Settings | text | Profile photo URL - **XSS risk** (image URL injection) |
| `currentpassword` | Settings | password | Password verification |
| `newpassword` | Settings | password | New password |

### Query String Parameters
| Parameter | Location | Notes |
|-----------|----------|-------|
| `username` | `/profile?username=...` | User profile display - **XSS risk** |
| `username` | `/friends?username=...` | Friends list display - **XSS risk** |
| `search` | `/users?search=...` | User search results - **XSS risk** |
| `search` | `/posts?search=...` | Post search results - **XSS risk** |
| `search` | `/messages?search=...` | Message search results - **XSS risk** |
| `content` | `/create_post?content=...` | Pre-fills post textarea - **XSS risk** |

### Hidden Form Fields
| Field Name | Location | Notes |
|-----------|----------|-------|
| `username` | Friendship forms | Friend request/accept/decline |
| `origin` | Friendship forms | Origin context (e.g., "requests") |

## Known User Accounts
- `mr_robot` - Current authenticated user
- `admin` - Administrator account
- `dpr` - Dread Pirate Roberts
- `heisenberg` - Heisenberg
- `rick` - Rick Sanchez
- `satoshi` - Satoshi Nakamoto
- `stark` - Ned Stark
- `anon1`, `anon2`, `anon3` - Anonymous accounts

## Security Observations
1. **No Anti-CSRF tokens** on any forms (login, signup, create_post, settings, requests, friend operations)
2. **Content Security Policy** not set (commented out in HTML source)
3. **Missing security headers**: X-Frame-Options, X-Content-Type-Options, SameSite cookie attribute
4. **Server version disclosure**: Werkzeug/3.0.6 Python/3.8.10
5. **Vulnerable JS library**: Bootstrap 4.0.0
6. **Application error disclosure**: `/posts` returns 500 with generic error message
7. **Stored XSS indicators**: Messages page shows pre-existing XSS payloads (`<script>alert(1)</script>`, `<img src=x onerror=alert(1)>`) in message content

## Technologies Identified
- **Backend**: Python 3.8.10, Werkzeug/3.0.6 (Flask WSGI)
- **Frontend**: Bootstrap 4.0.0, jQuery 3.6.4
- **Session**: Server-side session cookies (HttpOnly)
- **Database**: Not directly visible (likely SQLite/PostgreSQL based on Flask patterns)