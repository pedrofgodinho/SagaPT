# Hackergram Attack Surface

## Application Overview
Hackergram is a social media web application with user authentication, profiles, messaging, friend requests, posts, and settings.

## Authentication
- **Login:** `POST /login` with fields `username`, `password`
- **Signup:** `POST /signup` with fields `username`, `name`, `password`
- **Logout:** `GET /logout`
- **Credentials:** Form-based authentication configured (mr_robot/elliot123)

## Discovered Endpoints and Input Points

### GET Endpoints with Input Parameters

| Endpoint | Parameters | Description |
|----------|------------|-------------|
| `/` | None | Homepage/Feed |
| `/login` | None | Login page |
| `/signup` | None | Signup page |
| `/logout` | None | Logout |
| `/profile?username=XXX` | `username` | User profile page |
| `/friends?username=XXX` | `username` | Friends list |
| `/friends?username=XXX&search=XXX` | `username`, `search` | Friends list with search |
| `/messages?search=XXX` | `search` | Message search |
| `/direct_messages?username=XXX` | `username` | Direct messages with user |
| `/posts` | None | Posts feed |
| `/users?search=XXX` | `search` | User search |
| `/requests` | None | Friend requests page |
| `/requests?origin=XXX&username=XXX` | `origin`, `username` | Friend requests (origin: profile/requests) |
| `/create_post` | None | Create post page |
| `/edit_post?id=XXX` | `id` | Edit post page |
| `/delete_post?id=XXX` | `id` | Delete post page |
| `/settings` | None | Settings page |

### POST Endpoints with Input Parameters

| Endpoint | Fields | Description |
|----------|--------|-------------|
| `/login` | `username`, `password` | Authentication |
| `/signup` | `username`, `name`, `password` | Account creation |
| `/create_post` | Form fields (likely `content`, `title`) | Create new post |
| `/settings` | Form fields + file upload (multipart/form-data) | User settings |
| `/request_friend` | Form fields (likely `username`) | Send friend request |
| `/remove_friend` | Form fields (likely `username`) | Remove friend |
| `/remove_request` | Form fields (likely `username`) | Remove friend request |
| `/requests` | Form fields | Handle friend requests |

## Input Parameter Checklist

### Query String Parameters
- [ ] `username` - Used in `/profile`, `/friends`, `/direct_messages`
- [ ] `search` - Used in `/friends`, `/messages`, `/users`
- [ ] `id` - Used in `/edit_post`, `/delete_post`
- [ ] `origin` - Used in `/requests` (values: profile, requests)

### Form Fields
- [ ] `username` - Login, signup, friend requests
- [ ] `password` - Login, signup
- [ ] `name` - Signup
- [ ] File upload - Settings page (multipart/form-data)
- [ ] Post content fields - Create/edit post

## Notable Security Observations
- No CSRF tokens detected on forms
- Application error disclosure on `/posts` (500 Internal Server Error)
- Server information leakage (Werkzeug/3.0.6 Python/3.8.10)
- Missing security headers (CSP, X-Frame-Options, X-Content-Type-Options)
- Cookie without SameSite attribute
- Vulnerable JavaScript library (Bootstrap v4.0.0)

## Static Resources
- `/static/css/*`, `/static/js/*`, `/static/photos/*`
- `/robots.txt`, `/sitemap.xml`