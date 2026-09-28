# Attack Surface Mapping - Hackergram

## Discovered Endpoints (91 URLs)

### Authentication
| Method | URL | Parameters |
|--------|-----|------------|
| POST | /login | username, password |
| POST | /signup | username, name, password |
| GET | /logout | - |

### User Profiles
| Method | URL | Parameters |
|--------|-----|------------|
| GET | /profile | username |
| GET | /users | search |
| GET | /friends | username, search |
| GET | /friends?username=admin | username |
| GET | /friends?username=stark | username |
| GET | /friends?username=rick | username |
| GET | /friends?username=satoshi | username |
| GET | /friends?username=heisenberg | username |
| GET | /friends?username=dpr | username |
| GET | /friends?username=anon1 | username |
| GET | /friends?username=anon2 | username |
| GET | /friends?username=anon3 | username |
| GET | /friends?username=ZAP | username |

### Posts
| Method | URL | Parameters |
|--------|-----|------------|
| GET | /posts | search |
| GET | /create_post | - |
| POST | /create_post | title, content |
| GET | /edit_post | id |
| POST | /edit_post | title, content, id |
| GET | /delete_post | id |

### Messages
| Method | URL | Parameters |
|--------|-----|------------|
| GET | /messages | search |
| GET | /direct_messages | username |
| POST | /direct_messages | message, recipient |

### Requests
| Method | URL | Parameters |
|--------|-----|------------|
| GET | /requests | origin, username |
| POST | /request_friend | username |
| POST | /remove_friend | username |
| POST | /remove_request | username |

### Settings
| Method | URL | Parameters |
|--------|-----|------------|
| GET | /settings | - |
| POST | /settings | name, bio, photo (multipart) |

### Admin
| Method | URL | Parameters |
|--------|-----|------------|
| GET | /admin | - |

### Static Resources
- /static/css/bootstrap.min.css
- /static/css/main.css
- /static/js/jquery-3.6.4.min.js
- /static/js/bootstrap.min.js
- /static/photos/*.jpg, *.png

### Hidden/.git
- /.git/config (404)
- /.git (directory listing possible)

### Input Parameters Summary
- **GET Parameters:** username, search, id, origin
- **POST Form Fields:** username, password, name, title, content, message, recipient
- **File Upload:** photo (multipart/form-data on /settings)
- **Hidden Fields:** user_id in forms