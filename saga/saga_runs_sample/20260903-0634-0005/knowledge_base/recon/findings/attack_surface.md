# Hackergram - Complete Attack Surface

## Application Overview
Hackergram is a social media web application built on Werkzeug/3.0.6 Python/3.8.10. It features user authentication, profiles, friend management, direct messaging, posts, and search functionality.

---

## Unauthenticated Endpoints

| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/login` | GET | — | Login page / default landing page |
| `/login` | POST | `username`, `password` | Login form submission |
| `/signup` | GET | — | Signup page |
| `/signup` | POST | `username`, `name`, `password` | Signup form submission |
| `/sitemap.xml` | GET | — | Sitemap |
| `/robots.txt` | GET | — | Robots.txt |

---

## Authenticated Endpoints

### Profile & User Pages
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/` | GET | — | Homepage / Feed (shows posts from friends) |
| `/profile?username=` | GET | `username` | View user profile and their posts |
| `/users` | GET | `search` | Search users by username |
| `/users?search=` | GET | `search` | Search users by username |
| `/posts` | GET | `search` | Search posts (returned 500 error on access) |
| `/posts?search=` | GET | `search` | Search posts by content |

### Friend Management
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/friends` | GET | `username` (hidden), `search` | List friends with search by username |
| `/friends?username=` | GET | `username` | View a specific user's friends |
| `/friends?username=&search=` | GET | `username` (hidden), `search` | Search friends |
| `/request_friend` | POST | `username` | Send a friend request |
| `/remove_friend` | POST | `username` | Remove a friend |

### Friendship Requests
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/requests` | GET | — | View pending friendship requests |
| `/requests?origin=&username=` | GET | `origin` ("requests" or "profile"), `username` | View/act on friendship requests |

### Messaging
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/messages` | GET | `search` | Search/view all messages |
| `/messages?search=` | GET | `search` | Search messages by content |
| `/direct_messages` | GET | — | Direct messages page (default) |
| `/direct_messages?username=` | GET | `username` | Open direct message conversation with a user |
| `/direct_messages` | POST | `username`, `message` | Send a direct message |

### Post Management
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/create_post` | GET | `content` (prefills textarea) | New post creation page |
| `/create_post` | POST | `content` | Submit new post |
| `/edit_post?id=` | GET | `id` | Edit post page (GET form) |
| `/edit_post` | POST | `id`, `content` | Submit edited post |
| `/delete_post?id=` | GET | `id` | Delete post action |

### Settings
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/settings` | GET | — | User settings page |
| `/settings` | POST | `name`, `bio`, `photo` (file upload), `photo_url`, `currentpassword`, `newpassword` | Update profile settings (multipart/form-data) |

### Authentication
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/logout` | GET | — | Logout (redirects to homepage) |

### Static Assets
| Endpoint | Method | Input Parameters | Description |
|----------|--------|-----------------|-------------|
| `/static/css/main.css` | GET | — | Main stylesheet |
| `/static/css/bootstrap.min.css` | GET | — | Bootstrap CSS |
| `/static/js/jquery-3.6.4.min.js` | GET | — | jQuery library |
| `/static/js/bootstrap.min.js` | GET | — | Bootstrap JS |
| `/static/photos/*` | GET | — | User profile photos |

---

## Input Points Checklist

### Query String Parameters (GET)
- `username` — used on `/profile`, `/friends`, `/direct_messages`
- `search` — used on `/users`, `/posts`, `/messages`, `/friends`, `/direct_messages`
- `id` — used on `/edit_post`, `/delete_post`
- `origin` — used on `/requests` (values: "requests", "profile")
- `content` — used on `/create_post` (prefills textarea)

### Form Fields (POST - form/x-www-form-urlencoded)
- **Login:** `username`, `password`
- **Signup:** `username`, `name`, `password`
- **Create Post:** `content`
- **Edit Post:** `id`, `content`
- **Request Friend:** `username`
- **Remove Friend:** `username`
- **Remove Request:** `origin`, `username`
- **Direct Messages:** `username` (hidden), `message`
- **Settings:** `name`, `bio`, `photo` (file), `photo_url`, `currentpassword`, `newpassword`

### Hidden Form Fields
- `username` — present on `/friends` search form, `/direct_messages` send form, `/request_friend` from profile page

### File Upload
- `/settings` POST accepts `photo` as a file upload (multipart/form-data)

---

## Interesting Functionality
- **User Profiles:** Each user has a profile page with name, bio, photo, and their posts
- **Friend System:** Add/remove friends, send/receive friend requests
- **Direct Messaging:** Real-time-style chat with other users
- **Post Feed:** Homepage shows posts from all users (not just friends)
- **Search:** Search across users, posts, and messages
- **Post CRUD:** Create, edit, and delete posts (with ownership checks)
- **Settings:** Update name, bio, profile photo (file or URL), and password
- **Server Info Leak:** Werkzeug/3.0.6 Python/3.8.10 exposed in Server header
- **No CSRF Tokens:** ZAP flagged absence of Anti-CSRF tokens on all forms
- **Session Cookie:** HttpOnly session cookie without SameSite attribute