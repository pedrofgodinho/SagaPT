# FTP Directory Publicly Accessible - Information Disclosure

## Vulnerability Class
Information Disclosure / Sensitive File Exposure

## Endpoint
- GET http://juiceshop.local:3000/ftp/
- GET http://juiceshop.local:3000/ftp/acquisitions.md
- GET http://juiceshop.local:3000/ftp/incident-support.kdbx
- GET http://juiceshop.local:3000/ftp/coupons_2013.md.bak
- GET http://juiceshop.local:3000/ftp/encrypt.pyc
- GET http://juiceshop.local:3000/ftp/announcement_encrypted.md
- GET http://juiceshop.local:3000/ftp/quarantine/ (malware directory)

## Description
The `/ftp/` directory is publicly accessible without any authentication. It contains:
- **acquisitions.md**: Confidential acquisition plans with stock market impact information
- **incident-support.kdbx**: KeePass password database (3246 bytes, binary encrypted)
- **coupons_2013.md.bak**: Backup file with coupon data
- **encrypt.pyc**: Python compiled file
- **announcement_encrypted.md**: 369KB encrypted announcement
- **quarantine/**: Directory containing malware URL files (macOS, Linux, Windows variants)

## Evidence
- All files returned HTTP 200 with public access
- Directory listing at `/ftp/` shows all files with sizes and dates
- acquisitions.md returned markdown content labeled "confidential"
- incident-support.kdbx returned binary data (application/octet-stream)

## Severity
**HIGH** - Exposes confidential business documents, password database, and malware samples publicly.

## Impact
- Confidential business information exposure (acquisition plans)
- Password database accessible to any attacker
- Backup files may contain additional sensitive data