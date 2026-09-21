## FTP Server - Directory Traversal Attempt Reveals Stack Traces

**Vulnerability Class:** Information Disclosure via Error Messages
**Endpoint:** GET /ftp/../package.json and GET /ftp/../../etc/passwd
**Evidence:**
- Request: GET /ftp/../package.json → HTTP 200 with SPA HTML shell (not the actual file)
- Request: GET /ftp/../../etc/passwd → HTTP 200 with SPA HTML shell (not the actual file)
- Request: GET /ftp/..%2f..%2fetc%2fpasswd → HTTP 403 with error page containing full Express.js stack trace
  - Error: "ForbiddenError: Forbidden"
  - Stack trace reveals: `/juice-shop/node_modules/serve-index/index.js:129:19`
  - Stack trace reveals: `/juice-shop/build/server.js:280:9`
  - Stack trace reveals: `/juice-shop/build/lib/antiCheat.js:100:5`
- Request: GET /ftp/coupons_2013.md.bak → HTTP 403 with error page
  - Error: "Error: Only .md and .pdf files are allowed!"
  - Stack trace reveals: `/juice-shop/build/routes/fileServer.js:68:18`

**Impact:** While directory traversal is blocked, the error responses reveal internal file paths and the application's route structure. File type restrictions are enforced but the error messages confirm the application's internal architecture.

**Detection Payload:** GET /ftp/..%2f..%2fetc%2fpasswd → 403 with stack trace showing `/juice-shop/node_modules/serve-index/index.js:129:19`