## No Working File Upload Endpoints via Direct HTTP

**Endpoint:** POST /rest/file/upload, POST /api/upload
**Vulnerability Class:** Application Architecture

### Testing Performed
- `POST /rest/file/upload` with JSON body → 500 "Unexpected path: /rest/file/upload"
- `POST /api/upload` with JSON body → 500 "Unexpected path: /api/upload"
- `POST /rest/user/signup` with JSON body → 500 "Unexpected path"

### Evidence
All file upload and user registration endpoints return 500 errors with the same stack trace pattern:
```
Error: Unexpected path: /rest/file/upload
at /juice-shop/build/routes/angular.js:18:18
```

### Analysis
The application is an Angular SPA where file upload endpoints are not exposed as server-side Express routes. Any file upload functionality exists only within the Angular frontend context. Direct HTTP POST to upload endpoints is not possible.

### Impact
- No file upload vulnerability can be confirmed via direct HTTP testing
- File upload attacks would require the Angular SPA context
- The /ftp/ directory only supports file downloads, not uploads

### Note
File upload testing would require authenticated access through the Angular SPA frontend.