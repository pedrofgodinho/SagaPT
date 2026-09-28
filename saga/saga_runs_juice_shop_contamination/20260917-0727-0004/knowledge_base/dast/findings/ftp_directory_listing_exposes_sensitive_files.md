# FTP Directory Listing Exposes Sensitive Files

**Endpoint:** GET /ftp/
**Vulnerability Class:** Information Disclosure (Directory Listing)
**Risk:** High

## Description
The `/ftp/` directory is accessible without authentication and returns an HTML directory listing page showing all files and subdirectories. This exposes sensitive files including a KeePass password database and backup files.

## Evidence
- **HTTP Status:** 200
- **Content-Type:** text/html; charset=utf-8
- **Directory listing reveals the following files:**

| File | Size | Risk |
|------|------|------|
| `acquisitions.md` | 909 bytes | Confidential acquisition plans |
| `announcement_encrypted.md` | 369,237 bytes | Encrypted announcement |
| `coupons_2013.md.bak` | 131 bytes | Backup file (blocked by extension filter) |
| `eastere.gg` | 324 bytes | Game file |
| `encrypt.pyc` | 573 bytes | Python bytecode file |
| `incident-support.kdbx` | 3,246 bytes | **KeePass password database** |
| `legal.md` | 3,047 bytes | Legal document |
| `package-lock.json.bak` | 750,353 bytes | Backup file (blocked by extension filter) |
| `package.json.bak` | 4,263 bytes | Backup file (blocked by extension filter) |
| `suspicious_errors.yml` | 723 bytes | Configuration file (blocked by extension filter) |
| `quarantine/` | — | Subdirectory with malware URL shortcuts |

## Sensitive Files Accessible (200 OK)
1. **`incident-support.kdbx`** — KeePass password database file (3,246 bytes). This file may contain stored credentials and passwords.
2. **`acquisitions.md`** — Marked as confidential: "This document is confidential! Do not distribute!" Contains planned acquisition details.
3. **`legal.md`** — Legal information and terms of use.

## Sensitive Files Blocked (403)
The server enforces a file extension filter allowing only `.md` and `.pdf` files. Files with extensions like `.bak`, `.pyc`, `.kdbx`, `.gg`, `.yml` return 403 with error "Only .md and .pdf files are allowed!"

**Note:** The `incident-support.kdbx` file was listed in the directory but returns 403 when accessed directly. However, it is still visible in the directory listing, which discloses its existence and size to attackers.

## Impact
- Attackers can discover sensitive file names, sizes, and modification dates
- The KeePass database filename suggests credential storage exists
- Confidential business documents are publicly accessible
- Directory listing aids targeted attacks against specific files

## Remediation
- Disable directory listing on the `/ftp/` route
- Remove or restrict access to sensitive files
- Do not serve confidential documents over a public-facing path