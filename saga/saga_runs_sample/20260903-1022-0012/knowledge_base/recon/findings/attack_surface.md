# Hackergram Attack Surface

## Authentication Endpoints

### GET /login
- **Form Fields:**
  - `username` (text input)
  - `password` (password input)

### POST /login
- **Form Fields:**
  - `username`
  - `password`

### GET /signup
- **Form Fields:**
  - `username` (text input)
  - `name` (text input)
  - `password` (password input)

### POST /signup
- **Form Fields:**
  - `username`
  - `name`
  - `password`

### GET /logout
- No input parameters (link/button)

---

## Profile & User Management

### GET /profile?username={username}
- **URL Parameters:**
  - `username` (user-controllable, reflected in page)
- **Forms on Page:**
  - `POST /remove_request` with hidden fields: `username`, `origin`
  - `POST /request_friend` with hidden field: `username`

### GET /friends?username={username}&search={search}
- **URL Parameters:**
  - `username` (user-controllable, hidden in form)
  - `search` (search parameter for filtering friends)
- **Form Fields:**
  - `username` (hidden, pre-filled from URL)
  - `search` (text input)

### GET /users?search={search}
- **URL Parameters:**
  - `search` (search parameter for finding users)
- **Form Fields:**
  - `search` (text input)

---

## Messaging Features

### GET /messages?search={search}
- **URL Parameters:**
  - `search` (search parameter for filtering messages)
- **Form Fields:**
  - `search` (text input)

### GET /direct_messages?username={username}
- **URL Parameters:**
  - `username` (user-controllable, reflected in page)
- **Form Fields:**
  - `username` (hidden, pre-filled from URL)
  - `message` (textarea for composing messages)

### POST /direct_messages
- **Form Fields:**
  - `username` (hidden)
  - `message` (textarea)

---

## Posts & Content Management

### GET /create_post
- **URL Parameters:**
  - `content` (optional, pre-fills textarea)
- **Form Fields:**
  - `content` (textarea)

### POST /create_post
- **Form Fields:**
  - `content` (textarea)

### GET /edit_post?id={id}
- **URL Parameters:**
  - `id` (post ID, user-controllable)
- **Form Fields:**
  - `id` (hidden)
  - `content` (textarea, pre-filled with post content)

### POST /edit_post
- **Form Fields:**
  - `id` (hidden)
  - `content` (textarea)

### GET /delete_post?id={id}
- **URL Parameters:**
  - `id` (post ID, user-controllable)

### GET /posts
- No visible input parameters (currently returns 500 error)

---

## Settings & Profile Editing

### GET /settings
- **Form Fields:**
  - `name` (text input)
  - `bio` (textarea)
  - `photo` (file upload)
  - `photo_url` (text input)
  - `currentpassword` (password input)
  - `newpassword` (password input)

### POST /settings
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `name`
  - `bio`
  - `photo` (file upload)
  - `photo_url`
  - `currentpassword`
  - `newpassword`

---

## Friendship Management

### GET /requests
- **URL Parameters:**
  - `origin` (optional, e.g., "profile", "requests")
  - `username` (user-controllable)
- **Forms on Page:**
  - `POST /remove_request` with hidden fields: `username`, `origin`

### POST /request_friend
- **Form Fields:**
  - `username` (hidden)

### POST /remove_request
- **Form Fields:**
  - `username` (hidden)
  - `origin` (hidden)

---

## Static Resources (No User Input)
- `/static/css/main.css`
- `/static/css/bootstrap.min.css`
- `/static/js/jquery-3.6.4.min.js`
- `/static/js/bootstrap.min.js`
- `/static/photos/*` (icon.jpg, mrrobot.png, stark.jpg, dpr.jpg, heisenberg.png, default.jpg, rick.png, satoshi.png)
- `/robots.txt`
- `/sitemap.xml`

---

## Summary of All Input Points

| Endpoint | Method | Input Type | Parameter |
|----------|--------|------------|-----------|
| /login | GET/POST | Form | username, password |
| /signup | GET/POST | Form | username, name, password |
| /settings | GET/POST | Form | name, bio, photo, photo_url, currentpassword, newpassword |
| /create_post | GET/POST | Form | content |
| /edit_post | GET/POST | Form/URL | id, content |
| /delete_post | GET | URL | id |
| /profile | GET | URL | username |
| /friends | GET | URL/Form | username, search |
| /users | GET | URL/Form | search |
| /messages | GET | URL/Form | search |
| /direct_messages | GET/POST | URL/Form | username, message |
| /requests | GET | URL | origin, username |
| /request_friend | POST | Form | username |
| /remove_request | POST | Form | username, origin |
| /logout | GET | - | - |
| /posts | GET | - | - |