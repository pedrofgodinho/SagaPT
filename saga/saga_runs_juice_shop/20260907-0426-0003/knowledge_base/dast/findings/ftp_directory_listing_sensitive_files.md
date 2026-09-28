## Vulnerability Class
Information Disclosure - Sensitive Files Exposed via FTP Directory Listing

## Endpoint
`GET /ftp/`

## Evidence
The /ftp/ directory is publicly accessible and returns a directory listing containing:

| File | Size | Notes |
|------|------|-------|
| `quarantine/` | directory | Subdirectory with malware URL files |
| `acquisitions.md` | 909 bytes | Confidential acquisition plans |
| `announcement_encrypted.md` | 369,237 bytes | Encrypted announcement |
| `coupons_2013.md.bak` | 131 bytes | Backup file with coupons |
| `eastere.gg` | 324 bytes | Easter egg file |
| `encrypt.pyc` | 573 bytes | Python bytecode file (403 on direct access) |
| `incident-support.kdbx` | 3,246 bytes | KeePass database (403 on direct access) |
| `legal.md` | 3,047 bytes | Legal document |
| `package-lock.json.bak` | 750,353 bytes | Backup package lock file |
| `package.json.bak` | 4,263 bytes | Backup package.json |
| `suspicious_errors.yml` | 723 bytes | Error configuration (403 on direct access) |

The file extension filter allows only `.md` and `.pdf` files to be directly accessed. Files with other extensions (`.bak`, `.pyc`, `.kdbx`, `.yml`) return 403.

## Impact
- Backup files (.bak) may contain sensitive configuration or data
- `acquisitions.md` contains confidential business plans
- `incident-support.kdbx` is a KeePass database that may contain credentials (though not directly accessible)
- `package.json.bak` and `package-lock.json.bak` expose project dependencies

## Conclusion
The /ftp/ directory listing exposes sensitive files. While extension filtering prevents direct access to non-.md/.pdf files, the directory listing itself reveals the existence of backup files and sensitive documents. The `.bak` files listed in the directory cannot be downloaded directly (403), but their existence is disclosed.