# FTP Directory - Sensitive Files Exposed

## Finding
The `/ftp/` directory is publicly accessible with directory listing enabled, exposing sensitive files.

## Discovered Files
| File | Status | Sensitivity |
|------|--------|-------------|
| `/ftp/acquisitions.md` | 200 | Confidential - planned acquisitions (material non-public info) |
| `/ftp/announcement_encrypted.md` | 200 | Encrypted announcement (369KB) |
| `/ftp/coupons_2013.md.bak` | ? | Backup file - may contain old coupon codes |
| `/ftp/package-lock.json.bak` | ? | NPM package lock backup - dependency info |
| `/ftp/package.json.bak` | ? | NPM package backup - dependency info |
| `/ftp/incident-support.kdbx` | ? | KeePass database - may contain credentials |
| `/ftp/encrypt.pyc` | 403 | Python bytecode - only .md/.pdf allowed |
| `/ftp/suspicious_errors.yml` | 403 | YAML config - only .md/.pdf allowed |
| `/ftp/eastere.gg` | ? | Unknown file type |
| `/ftp/legal.md` | ? | Legal documents |
| `/ftp/quarantine/` | ? | Directory with malware URL files |
| `/ftp/quarantine/juicy_malware_macos_64.url` | ? | Malware download URLs |
| `/ftp/quarantine/juicy_malware_linux_amd_64.url` | ? | Malware download URLs |
| `/ftp/quarantine/juicy_malware_linux_arm_64.url` | ? | Malware download URLs |
| `/ftp/quarantine/juicy_malware_windows_64.exe.url` | ? | Malware download URLs |

## Extension Bypass
The FTP file server only allows `.md` and `.pdf` files. Attempts to access other extensions (`.pyc`, `.yml`) return 403. However, backup files (`.bak`) and other extensions may still be accessible.

## Impact
- Information disclosure of confidential business data
- Potential credential exposure via KeePass database
- Dependency information exposure
- Backup files may contain sensitive historical data

## Recommendation
Remove or restrict access to the FTP directory. Implement proper authentication for file downloads.