# Hackergram Attack Surface

## Technologies Identified
- **Backend**: Python 3.8.10 / Werkzeug 3.0.6 (Flask)
- **Frontend**: Bootstrap 4.0.0, jQuery 3.6.4
- **Session**: Cookie-based session (`session`), HttpOnly, no SameSite attribute
- **Security Headers Missing**: X-Frame-Options, Content-Security-Policy, X-Content-Type-Options
- **No CSRF tokens** on any form

## Users Discovered
`mr_robot` (current), `admin`, `satoshi`, `dpr`, `heisenberg`, `stark`, `rick`, `anon1`, `anon2`, `anon3`

## Endpoints and Input Parameters

### Authentication
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/login` | — | Login form page |
| POST | `/login` | `username`, `password` | Form-based login, no CSRF |
| GET | `/signup` | — | Registration page (redirects if logged in) |
| GET | `/logout` | — | Logout |

### User Profiles
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/profile?username=<user>` | `username` (query) | User profile page |

### Friends Management
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/friends?username=<user>` | `username` (query) | Friends list |
| GET | `/friends?username=<user>&search=<query>` | `username`, `search` (query) | Friends search form |
| POST | `/request_friend` | `username`, `origin` (form) | Send friend request, no CSRF |
| POST | `/remove_friend` | `username`, `origin` (form) | Remove friend, no CSRF |

### Friendship Requests
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/requests` | — | Pending friendship requests |
| GET | `/requests?origin=requests&username=<user>` | `origin`, `username` (query) | Process request from requests page |
| GET | `/requests?origin=profile&username=<user>` | `origin`, `username` (query) | Process request from profile page |
| POST | `/remove_request` | `username`, `origin` (form) | Remove request, no CSRF |

### Messaging
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/messages` | — | All messages page |
| GET | `/messages?search=<query>` | `search` (query) | Search messages by content |
| GET | `/direct_messages` | — | Direct messages index |
| GET | `/direct_messages?username=<user>` | `username` (query) | DM conversation with user |
| POST | `/direct_messages` | `username`, `message` (form) | Send DM, no CSRF |

### Posts
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/` | — | Homepage feed |
| GET | `/create_post` | `content` (query, pre-fills textarea) | New post form |
| POST | `/create_post` | `content` (form) | Create post, no CSRF |
| GET | `/edit_post?id=<id>` | `id` (query) | Edit post page |
| POST | `/edit_post` | `id`, `content` (form) | Update post, no CSRF |
| GET | `/delete_post?id=<id>` | `id` (query) | Delete post |
| GET | `/posts` | — | Search posts (returns 500 error) |

### User Search
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/users` | — | User list page |
| GET | `/users?search=<query>` | `search` (query) | Search users by username |

### Settings
| Method | Endpoint | Input Parameters | Notes |
|--------|----------|-----------------|-------|
| GET | `/settings` | — | User settings page |
| POST | `/settings` | `name`, `bio`, `photo` (file upload), `photo_url`, `currentpassword`, `newpassword` | Update profile, multipart/form-data, no CSRF |

### Static Assets
| Path | Type |
|------|------|
| `/static/css/bootstrap.min.css` | CSS |
| `/static/css/main.css` | CSS |
| `/static/js/jquery-3.6.4.min.js` | JavaScript |
| `/static/js/bootstrap.min.js` | JavaScript |
| `/static/photos/icon.jpg` | Image |
| `/static/photos/default.jpg` | Image |
| `/static/photos/mrrobot.png` | Image |
| `/static/photos/heisenberg.png` | Image |
| `/static/photos/dpr.jpg` | Image |
| `/static/photos/stark.jpg` | Image |
| `/static/photos/rick.png` | Image |

### Other
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/sitemap.xml` | Sitemap file |
| GET | `/robots.txt` | Returns 404 |

## Input Point Checklist (for DAST)
- [ ] `username` (query param on /profile, /friends, /direct_messages, /requests, /edit_post via hidden)
- [ ] `search` (query param on /friends, /messages, /users, /posts)
- [ ] `content` (form field on /create_post, /edit_post; query param on /create_post)
- [ ] `id` (query param on /edit_post, /delete_post)
- [ ] `name` (form field on /settings)
- [ ] `bio` (form field on /settings)
- [ ] `photo` (file upload on /settings)
- [ ] `photo_url` (form field on /settings)
- [ ] `currentpassword` (form field on /settings)
- [ ] `newpassword` (form field on /settings)
- [ ] `message` (form field on /direct_messages POST)
- [ ] `origin` (hidden form field on /request_friend, /remove_friend, /remove_request)

## Navigation Structure
```
/ (Homepage - feed)
├── /login (Sign In)
├── /signup (Sign Up)
├── /profile?username=<user> (User Profile)
│   └── /friends?username=<user> (Friends List)
│       └── /friends?username=<user>&search=<query> (Search Friends)
├── /requests (Friendship Requests)
│   └── /requests?origin=requests&username=<user>
│   └── /requests?origin=profile&username=<user>
├── /messages (All Messages)
│   └── /messages?search=<query> (Search Messages)
├── /direct_messages (Direct Messages)
│   └── /direct_messages?username=<user> (DM Conversation)
├── /create_post (Create New Post)
├── /edit_post?id=<id> (Edit Post)
├── /delete_post?id=<id> (Delete Post)
├── /users (User Directory)
│   └── /users?search=<query> (Search Users)
├── /posts (Search Posts - ERROR)
├── /settings (User Settings)
└── /logout (Logout)
```