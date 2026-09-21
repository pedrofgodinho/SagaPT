# Sensitive Data Exposure in FTP Directory

## Vulnerability Class
Information Disclosure / Sensitive Data Exposure

## Endpoint
`GET /ftp/{filename}`

## Description
Multiple sensitive files are publicly accessible in the `/ftp/` directory without authentication. These files contain confidential business information, encrypted credentials databases, and malware indicators.

## Accessible Sensitive Files

### 1. `/ftp/acquisitions.md` (200 OK, 909 bytes)
Contains confidential M&A information marked "This document is confidential! Do not distribute!" with details about planned competitor acquisitions that would impact stock market.

### 2. `/ftp/incident-support.kdbx` (200 OK, 3246 bytes)
KeePass password database file accessible without authentication. This file likely contains stored credentials for incident support systems.

### 3. `/ftp/announcement_encrypted.md` (200 OK, 369237 bytes)
Large file (369KB) containing encrypted data represented as very large numeric strings (appears to be RSA-encrypted data with 600+ digit numbers).

### 4. `/ftp/legal.md` (200 OK, 3047 bytes)
Legal information and terms of use document.

### 5. Quarantine directory (`/ftp/quarantine/`)
Contains 4 malware URL shortcut files:
- `juicy_malware_linux_amd_64.url` → `https://github.com/juice-shop/juicy-malware/raw/master/juicy_malware_linux_amd_64`
- `juicy_malware_windows_64.exe.url` → `https://github.com/juice-shop/juicy-malware/raw/master/juicy_malware_windows_64.exe`
- `juicy_malware_linux_arm_64.url`
- `juicy_malware_macos_64.url`

### 6. `/ftp/coupons_2013.md.bak` (accessible via extension bypass)
Backup file with 131 bytes of content (appears to be encoded/cipher text).

### 7. `/ftp/encrypt.pyc` (accessible via extension bypass)
Python compiled module revealing internal filenames: `encrypt.py`, `announcement.mdt`, `announcement_encrypted.mdt`, `confidential_document`, `encrypted_document`.

## Impact
- KeePass database exposure could lead to credential compromise
- Confidential M&A documents exposed to public
- Malware download links publicly accessible
- Backup files may contain historical sensitive data
- Encrypted data exposure could aid cryptographic attacks

## Mitigation
- Require authentication for FTP directory access
- Remove or restrict access to sensitive files (.kdbx, .bak, .pyc)
- Remove malware shortcut files from publicly accessible locations
- Apply proper access controls on all FTP content