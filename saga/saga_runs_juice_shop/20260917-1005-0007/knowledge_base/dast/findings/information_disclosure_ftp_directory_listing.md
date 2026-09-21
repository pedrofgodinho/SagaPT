# Information Disclosure: FTP Directory Listing

## Vulnerability Class
Information Disclosure / Security Misconfiguration

## Endpoint
`GET /ftp/`

## Evidence
- **HTTP Status**: 200 OK
- **Content-Type**: `text/html; charset=utf-8`
- **Content-Length**: 11324 bytes
- The `serve-index` middleware generates an HTML directory listing showing all files in `/ftp/`
- Directory listing reveals:
  - `quarantine/` (subdirectory with malware URL files)
  - `acquisitions.md` (confidential document)
  - `announcement_encrypted.md` (369KB encrypted content)
  - `coupons_2013.md.bak` (backup file)
  - `eastere.gg` (easter egg file)
  - `encrypt.pyc` (Python compiled file)
  - `encrypt.pyc` (Python compiled file)
  - `incident-support.kdbx` (KeePass database)
  - `legal.md` (legal document)
  - `package-lock.json.bak` (NPM backup)
  - `package.json.bak` (NPM backup)
  - `suspicious_errors.yml` (suspicious errors config)

## Impact
The directory listing exposes the complete file inventory of the FTP directory, enabling attackers to:
- Discover sensitive files they might not have known about
- Understand the application's data storage structure
- Target specific files for download (e.g., the KeePass database, backup files)

## Detection Payload
`GET /ftp/` → Returns HTML directory listing with all files and their sizes