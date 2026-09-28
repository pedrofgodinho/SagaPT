# FTP Directory Information Disclosure

## Vulnerability Class
Information Disclosure

## Endpoint
GET /ftp/

## Evidence
The `/ftp/` directory returns a full directory listing (HTTP 200) with no authentication required. The listing reveals:

- `acquisitions.md` (909 bytes) — confidential M&A plans
- `announcement_encrypted.md` (369,237 bytes)
- `coupons_2013.md.bak` (131 bytes) — backup file
- `eastere.gg` (324 bytes)
- `encrypt.pyc` (Python bytecode)
- `incident-support.kdbx` (3,246 bytes) — **KeePass password database**
- `legal.md` (3,047 bytes)
- `package-lock.json.bak` — backup file
- `package.json.bak` — backup file
- `quarantine/` directory with malware URL files

## Impact
An attacker can enumerate all files in the FTP directory, identify sensitive files, and directly access publicly served `.md` files containing confidential business information (e.g., acquisitions document marked "confidential").

## Risk
Medium — Public directory listing exposes sensitive file names and allows access to confidential documents.