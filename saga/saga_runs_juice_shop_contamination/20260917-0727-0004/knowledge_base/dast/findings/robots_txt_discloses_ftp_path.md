# robots.txt Discloses Sensitive FTP Path

**Endpoint:** GET /robots.txt
**Vulnerability Class:** Information Disclosure
**Risk:** Low

## Description
The `/robots.txt` file explicitly disallows the `/ftp` path, which inadvertently informs attackers that a sensitive FTP directory exists at that location.

## Evidence
- **HTTP Status:** 200
- **Content-Type:** text/plain; charset=utf-8
- **robots.txt contents:**
```
User-agent: *
Disallow: /ftp
```

## Impact
- Confirms the existence of the `/ftp/` directory to attackers
- The `/ftp/` directory contains sensitive files including a KeePass password database, confidential acquisition plans, and backup files
- While robots.txt is intended to prevent crawler indexing, it serves as a map of sensitive paths for malicious actors

## Remediation
- Remove the `/ftp` disallow rule from robots.txt
- Alternatively, restrict access to `/ftp/` at the server level so the directory is not accessible at all