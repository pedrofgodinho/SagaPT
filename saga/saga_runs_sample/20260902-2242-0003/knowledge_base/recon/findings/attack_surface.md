# Hackergram Attack Surface

## Application Overview
- **Type:** Social media application (Python/Werkzeug)
- **Authentication:** Form-based login
- **Known Users:** admin, mr_robot, rick, stark, heisenberg, satoshi, dpr, anon1, anon2, anon3

## Unauthenticated Endpoints

### GET
- `/` — Homepage (redirects to login if not authenticated)
- `/login` — Sign In page
- `/signup` — Sign Up page
- `/static/css/bootstrap.min.css` — Static CSS
- `/static/css/main.css` — Static CSS
- `/static/js/jquery-3.6.4.min.js` — Static JS
- `/static/js/bootstrap.min.js` — Static JS
- `/static/photos/*` — Static images
- `/robots.txt` — Robots file
- `/sitemap.xml` — Sitemap

### POST
- `/login` — Authentication form
  - `username` (text)
  - `password` (password)
- `/signup` — Registration form
  - `username` (text)
  - `name` (text)
  - `password` (password)

## Authenticated Endpoints

### GET
- `/` — Homepage (feed of posts)
  - No query parameters
- `/create_post` — New post page
  - `content` (query param, pre-fills textarea)
- `/settings` — Account settings page
- `/requests` — Friendship requests page
- `/friends` — Friends list page
  - `username` (query param, required)
  - `search` (query param, search by username)
- `/messages` — Search messages page
  - `search` (query param, search by content)
- `/direct_messages` — Direct messages page
  - `username` (query param, required)
- `/users` — Search users page
  - `search` (query param, search by username)
- `/posts` — Search posts page (note: returned 500 error during spider)
- `/profile` — User profile page
  - `username` (query param, required)
- `/edit_post` — Edit post page
  - `id` (query param, required)
- `/delete_post` — Delete post page
  - `id` (query param, required)
- `/logout` — Logout endpoint
- `/remove_friend` — Remove friend endpoint
- `/remove_request` — Remove friend request endpoint
- `/request_friend` — Send friend request endpoint

### POST
- `/create_post` — Create new post
  - `content` (textarea, post content)
- `/settings` — Update account settings
  - `name` (text, display name)
  - `bio` (textarea, profile bio)
  - `photo` (file upload, profile photo)
  - `photo_url` (text, image URL)
  - `currentpassword` (password, current password)
  - `newpassword` (password, new password)
- `/edit_post` — Edit existing post
  - `id` (hidden field, post ID)
  - `content` (textarea, updated post content)
- `/remove_friend` — Remove a friend
  - `username` (hidden field, friend's username)
- `/remove_request` — Remove a friend request
  - `username` (hidden field, requester's username)
  - `origin` (hidden field, "profile" or "requests")
- `/request_friend` — Send a friend request
  - `username` (hidden field, target username)

## Input Parameter Summary (Flat Checklist)

| Endpoint | Method | Parameter | Type | Description |
|----------|--------|-----------|------|-------------|
| `/login` | POST | `username` | text | Login username |
| `/login` | POST | `password` | password | Login password |
| `/signup` | POST | `username` | text | New username |
| `/signup` | POST | `name` | text | Display name |
| `/signup` | POST | `password` | password | New password |
| `/create_post` | POST | `content` | textarea | Post content |
| `/settings` | POST | `name` | text | Display name |
| `/settings` | POST | `bio` | textarea | Profile bio |
| `/settings` | POST | `photo` | file | Profile photo upload |
| `/settings` | POST | `photo_url` | text | Profile photo URL |
| `/settings` | POST | `currentpassword` | password | Current password |
| `/settings` | POST | `newpassword` | password | New password |
| `/edit_post` | POST | `id` | hidden | Post ID |
| `/edit_post` | POST | `content` | textarea | Updated content |
| `/remove_friend` | POST | `username` | hidden | Friend username |
| `/remove_request` | POST | `username` | hidden | Requester username |
| `/remove_request` | POST | `origin` | hidden | Origin ("profile"/"requests") |
| `/request_friend` | POST | `username` | hidden | Target username |
| `/` | GET | (none) | — | Homepage |
| `/create_post` | GET | `content` | query | Pre-fill content |
| `/friends` | GET | `username` | query | Target user |
| `/friends` | GET | `search` | query | Search friends |
| `/messages` | GET | `search` | query | Search messages |
| `/direct_messages` | GET | `username` | query | Target user |
| `/users` | GET | `search` | query | Search users |
| `/posts` | GET | (none) | — | Search posts |
| `/profile` | GET | `username` | query | Target user |
| `/edit_post` | GET | `id` | query | Post ID |
| `/delete_post` | GET | `id` | query | Post ID |
| `/logout` | GET | (none) | — | Logout |

## Notable Findings
- **No CSRF tokens** detected on any forms
- **Application Error Disclosure:** `/posts` returns 500 Internal Server Error with debug messages
- **Server version leak:** Werkzeug/3.0.6 Python/3.8.10
- **Missing security headers:** No X-Frame-Options, CSP, or X-Content-Type-Options
- **Cookie without SameSite attribute** on session cookie
- **Vulnerable JS Library:** Bootstrap v4.0.0
- **User-controllable HTML attributes** detected on profile pages (potential XSS vector)
- **Sensitive info in URL:** `username` parameter visible in profile URLs