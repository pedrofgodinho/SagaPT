## Path Traversal on /ftp/ - Blocked by Extension Filter

**Endpoint:** GET /ftp/
**Vulnerability Class:** Path Traversal (attempted but blocked)

### Tests Performed
- `GET /ftp/../../../etc/passwd` → 403 ForbiddenError: Forbidden
- `GET /ftp/../../../etc/shadow` → 403 ForbiddenError: Forbidden
- `GET /ftp/../../../windows/system32/drivers/etc/hosts` → 403 ForbiddenError: Forbidden
- `GET /ftp/..%252f..%252f..%252f..%252fetc%252fpasswd` (double-encoded) → 403 Error: Only .md and .pdf files are allowed!
- `GET /ftp/....//....//....//etc/passwd` → 403 Error: Only .md and .pdf files are allowed!
- `GET /ftp/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd` → 200 (returned main page HTML, not file contents)

### Evidence
The FTP file server enforces an extension whitelist allowing only `.md` and `.pdf` files. Attempts to access files with other extensions (including traversal attempts) return 403 with error messages:
- "ForbiddenError: Forbidden" (from serve-index directory listing)
- "Error: Only .md and .pdf files are allowed!" (from fileServer.js verification)

### Stack Trace Disclosure
Error responses include full stack traces showing internal paths:
- `/juice-shop/build/routes/fileServer.js:68:18`
- `/juice-shop/node_modules/serve-index/index.js:139:16`

### Conclusion
Path traversal is **blocked** by the extension filter. The application validates file extensions before serving content. However, the error messages reveal internal file paths which is a secondary concern.

### Note
The application error disclosure (stack traces in error responses) is a separate finding already documented.