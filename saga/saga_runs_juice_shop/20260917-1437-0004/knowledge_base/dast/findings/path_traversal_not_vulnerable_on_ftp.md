# Path Traversal Not Vulnerable on /ftp/ Endpoint

**Vulnerability Class:** Path Traversal (Negative Finding)

**Affected Endpoints:**
- GET /ftp/

**Evidence:**
Path traversal attempts on /ftp/ were tested with multiple techniques:

1. `GET /ftp/../../etc/passwd` → 200 (SPA shell - route falls through to Angular SPA catch-all)
2. `GET /ftp/..%2f..%2f..%2fetc%2fpasswd` → 403 ForbiddenError: Forbidden
3. `GET /ftp/%2e%2e/%2e%2e/%2e%2e/etc/passwd` → 200 (SPA shell - route falls through)

**Detection Payloads:**
```
GET /ftp/../../etc/passwd → 200 (SPA shell, not /etc/passwd content)
GET /ftp/..%2f..%2f..%2fetc%2fpasswd → 403 Forbidden
GET /ftp/%2e%2e/%2e%2e/%2e%2e/etc/passwd → 200 (SPA shell, not /etc/passwd content)
```

**Impact:**
- Path traversal is NOT exploitable on the /ftp/ endpoint
- The application either blocks traversal attempts (403) or falls through to the Angular SPA catch-all route
- The FTP directory listing (already confirmed as a separate finding) exposes file names but does not allow reading arbitrary system files

**Notes:**
- The /ftp/ directory is publicly accessible with directory listing (already recorded)
- The application restricts access to specific file extensions (.md, .pdf)
- Path traversal protection is in place but the directory listing itself is the information disclosure risk