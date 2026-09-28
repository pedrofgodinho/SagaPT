## Information Disclosure - Sensitive FTP Files and Error Pages

**Vulnerability Class**: Information Disclosure
**Endpoint**: 
- GET /ftp/acquisitions.md
- GET /ftp/legal.md
- GET /ftp/package.json.bak (403 error page)
- GET /nonexistent-path (403 error pages)

**Description**:
The /ftp/ directory is publicly accessible and contains sensitive files:
- `/ftp/acquisitions.md` returns 200 with confidential acquisition plans marked "Do not distribute!"
- `/ftp/legal.md` returns 200 with legal document content
- `/ftp/package.json.bak` returns 403 but the error page reveals sensitive information

**Error Page Information Leakage**:
The 403 error page for disallowed file extensions reveals:
- Application name: "OWASP Juice Shop (Express ^4.22.1)"
- Full Node.js stack trace with file paths: `/juice-shop/build/routes/fileServer.js:68:18`
- Express version: ^4.22.1
- Internal directory structure: `/juice-shop/build/routes/`

**Evidence**:
- `GET /ftp/acquisitions.md` → 200, body contains "This document is confidential! Do not distribute!"
- `GET /ftp/package.json.bak` → 403, body contains full stack trace and Express version
- `GET /nonexistent-path-12345` → 403 error pages also reveal Express version and stack traces

**Risk**: Medium - Reveals application technology stack, version, and internal file paths that aid further attacks.