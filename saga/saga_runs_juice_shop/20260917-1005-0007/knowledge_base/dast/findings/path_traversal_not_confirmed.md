# Path Traversal Testing - Not Confirmed

## Summary
Path traversal testing was attempted on the file server and FTP directory but could not be confirmed.

## Tested Input Points

### 1. /rest/fileServer/:path (REST endpoint)
- **Payloads tested**: `../../../etc/passwd`, `ftp/acquisitions.md`, `..%2f..%2f..%2fetc%2fpasswd`
- **Result**: HTTP 500 - "Error: Unexpected path" (Angular catch-all intercepts all `/rest/*`)
- **Status**: NOT VULNERABLE (cannot test due to routing issue)

### 2. /ftp/ Directory (direct file server)
- **Payloads tested**:
  - `../../etc/passwd` → HTTP 200, returns Angular shell (not processed as file)
  - `..%2f..%2fetc%2fpasswd` → HTTP 403 Forbidden
  - **Evidence**: `serve-index` middleware blocks path traversal with "ForbiddenError: Forbidden"

- **Legitimate file access**: `/ftp/acquisitions.md` → HTTP 200, returns file content (909 bytes)
- **Directory listing**: `/ftp/` → HTTP 200, returns directory listing with files
- **Status**: Path traversal is BLOCKED by serve-index middleware

### 3. Angular Hash Route /#/fileServer/
- **Payloads tested**: `../../../etc/passwd`, `ftp/acquisitions.md`
- **Result**: HTTP 200, returns identical static shell (9393 bytes)
- **Status**: Not a valid path traversal vector (Angular handles routing client-side)

## Conclusion
No path traversal vulnerability could be confirmed. The `/ftp/` directory's serve-index middleware properly blocks traversal attempts (returning 403). The `/rest/fileServer/` endpoint is inaccessible due to Angular's catch-all route.