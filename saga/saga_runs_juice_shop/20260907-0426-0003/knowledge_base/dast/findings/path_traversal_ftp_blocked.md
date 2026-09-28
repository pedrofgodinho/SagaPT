## Vulnerability Class
Path Traversal (Directory Traversal) - NOT PRESENT

## Endpoint
`GET /ftp/` and related file server routes

## Test Payloads Attempted
1. `/ftp/../../etc/passwd` → 200 (returned main HTML page, not /etc/passwd)
2. `/ftp/..%2f..%2fetc%2fpasswd` → 403 ForbiddenError: Forbidden
3. `/ftp/../../../etc/hosts` → 200 (returned main HTML page)
4. `/ftp/..%252f..%252fetc%252fpasswd` (double-encoded) → 403 "Only .md and .pdf files are allowed!"
5. `/ftp/..%2f..%2f..%2fetc%2fpasswd` → 403 ForbiddenError: Forbidden
6. `/ftp/test.md.bak` → 403 "Only .md and .pdf files are allowed!"
7. `/ftp/package.json.bak` → 403 "Only .md and .pdf files are allowed!"

## Evidence
All path traversal attempts were blocked. The application:
- Properly sanitizes `../` sequences in file paths
- Enforces file extension filtering (only .md and .pdf allowed)
- Returns 403 Forbidden for traversal attempts that escape the /ftp/ directory
- Extension bypass attempts (.bak, .pyc) are blocked with 403

## Conclusion
No path traversal vulnerability confirmed on the /ftp/ directory. The file server properly restricts access to files within the /ftp/ directory and enforces extension filtering.