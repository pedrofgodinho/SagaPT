# Path Traversal on /ftp/ File Server

## Test Results
| Payload | Status | Result |
|---------|--------|--------|
| `/ftp/..%2f..%2f..%2fetc%2fpasswd` | 403 | Forbidden - extension filter blocks |
| `/ftp/../../etc/hosts` | 200 | Returns Angular SPA shell (not actual file) |
| `/ftp/../../../etc/passwd` | 200 | Returns Angular SPA shell (not actual file) |
| `/ftp/..%252f..%252f..%252fetc%252fpasswd` | 403 | "Only .md and .pdf files are allowed!" |

## Analysis
- **Double-encoded traversal** (`%252f`): Blocked by file extension whitelist - returns 403 with "Only .md and .pdf files are allowed!"
- **Plain `../../` traversal**: Returns the Angular SPA shell (200) because the Angular router intercepts these paths before they reach the file server. The SPA serves the same shell for all unmatched routes.
- **URL-encoded `..%2f`**: Returns 403 Forbidden - blocked by the file server's path traversal protection

## Conclusion
The file server has path traversal protection:
1. Extension whitelist (only .md and .pdf allowed) - blocks double-encoded attempts
2. Path traversal detection - blocks URL-encoded traversal attempts
3. The plain `../../` paths returning SPA shell is not a true vulnerability - they don't expose files, just the Angular shell

## Sensitive Files Still Accessible
- `/ftp/acquisitions.md` (200) - Confidential acquisition plans
- `/ftp/legal.md` (200) - Legal information
- These are intentionally accessible but contain sensitive content