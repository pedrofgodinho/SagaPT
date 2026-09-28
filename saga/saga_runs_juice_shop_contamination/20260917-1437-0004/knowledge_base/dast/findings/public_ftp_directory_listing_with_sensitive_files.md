# Public FTP Directory Listing with Sensitive Files

**Endpoint:** `GET /ftp/` and `GET /ftp/quarantine/`
**Vulnerability Class:** Sensitive Information Disclosure

## Evidence
The FTP directory is publicly accessible without authentication. Directory listing reveals:
- `/ftp/acquisitions.md` - Confidential acquisition plans
- `/ftp/announcement_encrypted.md` - Large encrypted file (369KB)
- `/ftp/coupons_2013.md.bak` - Backup coupon data
- `/ftp/eastere.gg` - Easter egg file
- `/ftp/encrypt.pyc` - Python bytecode file
- `/ftp/incident-support.kdbx` - KeePass password database (3246 bytes)
- `/ftp/package.json.bak` - Package dependencies backup
- `/ftp/package-lock.json.bak` - Lock file backup
- `/ftp/quarantine/juicy_malware_linux_amd_64.url` - Malware URL file
- `/ftp/quarantine/juicy_malware_linux_arm_64.url` - Malware URL file
- `/ftp/quarantine/juicy_malware_macos_64.url` - Malware URL file
- `/ftp/quarantine/juicy_malware_windows_64.exe.url` - Malware URL file

## Detection
```
GET /ftp/
Response: 200 OK
Body: HTML directory listing with all file names, sizes, and dates
```

## Impact
Attackers can discover and download sensitive files including:
- Confidential business documents (acquisitions plans)
- Password database (KeePass file)
- Backup files with potential credentials or dependencies
- Malware URL files (potential social engineering vector)

## Notes
The application restricts direct file access to `.md` and `.pdf` files only (403 for other extensions), but the directory listing itself reveals all files.