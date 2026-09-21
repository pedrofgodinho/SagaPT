## Path Traversal Blocked on /ftp/ Directory

**Endpoint:** `GET http://juiceshop.local:3000/ftp/`
**Vulnerability Class:** Informational — Access Control

### Testing Performed
- Direct traversal: `/ftp/../../etc/passwd` → 200 (SPA shell, not file content)
- Double-encoded traversal: `/ftp/..%252f..%252f..%252fetc%252fpasswd` → 403
- Null byte bypass: `/ftp/..%252f..%252f..%252fetc%252fpasswd%00.md` → 400
- Backslash traversal: `/ftp/..%255c..%255c..%255cetc%255cpasswd` → 403
- Traversal with .md extension: `/ftp/..%2f..%2f..%2fetc%2fpasswd.md` → 403
- Sensitive file access: `/ftp/.env` → 403 "Only .md and .pdf files are allowed!"
- Sensitive file access: `/ftp/package.json` → 403 "Only .md and .pdf files are allowed!"

### Evidence
- Path traversal attempts are blocked by the server with 403 responses.
- Error message: `Error: Only .md and .pdf files are allowed!`
- Enforced at `/juice-shop/build/routes/fileServer.js:68:18` in the `verify` middleware.

### Analysis
The /ftp/ directory has a file extension whitelist restricting access to `.md` and `.pdf` files. Path traversal attempts are blocked at the route level.

### Impact
No path traversal vulnerability confirmed. The directory is properly secured against traversal attacks.