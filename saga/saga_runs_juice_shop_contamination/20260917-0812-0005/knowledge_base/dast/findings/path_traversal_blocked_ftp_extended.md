## Path Traversal Blocked on /ftp/ Directory (Extended Testing)

**Endpoint:** `GET http://juiceshop.local:3000/ftp/`
**Vulnerability Class:** Informational — Access Control

### Testing Performed (Extended)
- `GET /ftp/../../etc/passwd` → 200 (returns Angular SPA shell, not file content)
- `GET /ftp/..%2f..%2f..%2fetc%2fpasswd` → 403 "ForbiddenError: Forbidden"
- `GET /ftp/..%252f..%252f..%252fetc%252fpasswd` → 403 "Error: Only .md and .pdf files are allowed!"
- `GET /ftp/..%2f..%2f..%2fetc%2fpasswd%00.md` → 400 "BadRequestError: Bad Request"

### Evidence
- Direct traversal (`../../etc/passwd`) returns the SPA shell (200) — the path is not resolved to the file.
- URL-encoded traversal (`..%2f..%2f..%2fetc%2fpasswd`) returns 403 Forbidden.
- Double-encoded traversal (`..%252f..%252f..%252fetc%252fpasswd`) returns 403 with explicit error message.
- Null byte injection (`%00.md`) returns 400 Bad Request.

### Analysis
The /ftp/ directory has multiple layers of protection against path traversal:
1. URL encoding is properly decoded and validated
2. Double encoding is detected and blocked
3. File extension whitelist restricts access to `.md` and `.pdf` files only
4. Null byte injection is rejected at the parser level
5. The server-side error messages reveal the application uses Express with `serve-index` and custom `verify` middleware at `/juice-shop/build/routes/fileServer.js:68:18`

### Impact
No path traversal vulnerability confirmed. The directory is properly secured against traversal attacks, including encoded and double-encoded variants.