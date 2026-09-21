# Application Error Disclosure: Stack Trace with Internal File Paths

## Vulnerability Class
Information Disclosure / Security Misconfiguration

## Endpoints Tested
- `GET /redirect?url=<any>` — returns 500 with full stack trace
- `GET /ftp/suspicious_errors.yml` — returns 403 with full stack trace
- `GET /ftp/..%c0%af..%c0%af..%c0%afetc%c0%afpasswd` — returns 400 with full stack trace

## Evidence
All error responses include Express stack traces revealing internal file paths:

**Redirect endpoint (500):**
```
TypeError: Cannot read properties of undefined (reading 'includes')
at Object.isRedirectAllowed (/juice-shop/build/lib/insecurity.js:157:34)
at /juice-shop/build/routes/redirect.js:47:22
```

**File server extension filter (403):**
```
Error: Only .md and .pdf files are allowed!
at verify (/juice-shop/build/routes/fileServer.js:68:18)
at /juice-shop/build/routes/fileServer.js:52:13
```

**UTF-8 encoding bypass attempt (400):**
```
URIError: Failed to decode param '/ftp/..%C0%AF..%C0%AF..%C0%AFetc%C0%AFpasswd'
at decodeURIComponent (<anonymous>)
at decode_param (/juice-shop/node_modules/express/lib/router/layer.js:172:12)
```

## Impact
Stack traces reveal:
- Internal project directory structure (`/juice-shop/build/...`)
- Specific file paths and line numbers in application code
- Node.js module paths confirming Express.js usage
- Function names (`isRedirectAllowed`, `verify`, `decode_param`)

This information aids attackers in understanding the application architecture and crafting more targeted attacks.

## Detection
Every error response from the redirect endpoint, file server, and URI decoder includes a full Express stack trace with absolute file paths to application code files.

## Notes
This was confirmed on 9 separate requests across 3 different endpoints. The responses were byte-for-byte identical within each endpoint type, confirming the error handling is consistent.