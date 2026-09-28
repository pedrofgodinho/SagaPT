# Hackergram - Complete Penetration Testing Assessment Summary

## Target
http://www.hackergram.com

## Technology Stack
- **Backend:** Python 3.8.10 / Werkzeug 3.0.6 (Flask)
- **Database:** MySQL 8.0.42
- **Frontend:** Bootstrap 4.0.0, jQuery 3.6.4
- **Session:** HTTP cookies (Base64-encoded JSON, no SameSite attribute)

## Critical Findings

### 1. SQL Injection (CRITICAL)
- **Affected:** `/profile?username`, `/users?search`, `/posts?search`, `/friends?search`
- **Type:** Error-based (MySQL updatexml())
- **Impact:** Full database access, all user credentials extracted
- **Extracted Credentials:**
  | Username | Password |
  |----------|----------|
  | admin | 1_4m_Th3_4dm1n |
  | anon1 | 1 |
  | anon2 | 2 |
  | anon3 | 3 |
  | dpr | silk-road |
  | heisenberg | walter1958 |
  | mr_robot | elliot123 |

### 2. Reflected XSS (HIGH)
- **Affected:** `/users?search`, `/friends?username`
- **Type:** Reflected Cross-Site Scripting
- **Impact:** Arbitrary JavaScript execution in victim's browser

### 3. Stored XSS (HIGH)
- **Affected:** `/create_post` (title field)
- **Type:** Stored Cross-Site Scripting
- **Impact:** Persistent XSS affecting all visitors to the affected post

### 4. Broken Access Control / IDOR (HIGH)
- **Affected:** `/profile?username`, `/direct_messages?username`, `/delete_post?id`, `/edit_post?id`
- **Type:** Insecure Direct Object References
- **Impact:** Users can access other users' profiles, messages, and delete/edit other users' posts

## Medium Findings

### 5. Missing Security Headers
- No Content-Security-Policy header
- No X-Frame-Options header
- No X-Content-Type-Options header

### 6. Missing Anti-CSRF Tokens
- All forms lack CSRF protection tokens
- Affected: login, signup, create_post, edit_post, settings, request_friend, remove_friend, remove_request, direct_messages

### 7. Cookie Security Issues
- Session cookie lacks SameSite attribute
- Session cookie is HttpOnly (good) but not Secure

### 8. Server Information Disclosure
- Server header reveals: `Werkzeug/3.0.6 Python/3.8.10`
- Application error messages reveal MySQL version and syntax details

### 9. Vulnerable JavaScript Library
- Bootstrap 4.0.0 has known vulnerabilities

### 10. Debug Error Messages
- SQL errors are displayed in full, aiding attacker reconnaissance

## Attack Surface
- 91 discovered URLs
- Multiple input parameters: username, search, id, title, content, message
- File upload endpoint at `/settings` (photo field)
- REST-like API endpoints for social features

## Recommendations
1. **SQL Injection:** Use parameterized queries/prepared statements everywhere
2. **XSS:** Implement output encoding/escaping on all user inputs
3. **Access Control:** Implement proper authorization checks on all endpoints
4. **CSRF:** Add anti-CSRF tokens to all forms
5. **Security Headers:** Add CSP, X-Frame-Options, X-Content-Type-Options
6. **Error Handling:** Return generic error messages, not SQL details
7. **Password Storage:** Use bcrypt/argon2 instead of plaintext passwords
8. **Cookie Security:** Add SameSite=Strict, Secure flags