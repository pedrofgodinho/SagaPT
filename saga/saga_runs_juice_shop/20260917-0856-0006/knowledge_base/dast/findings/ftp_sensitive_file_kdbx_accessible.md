# FTP Sensitive File Access — KeePass Database

## Vulnerability Class
Information Disclosure / Sensitive File Exposure

## Endpoint
GET /ftp/incident-support.kdbx

## Evidence
The KeePass database file is publicly accessible:
```
GET /ftp/incident-support.kdbx → HTTP 200
Content-Type: application/octet-stream
Content-Length: 3246
```

The file was returned as binary data (KeePass 2.x database format). Additionally, the FTP server has file extension restrictions ("Only .md and .pdf files are allowed!") but the `.kdbx` file bypassed this restriction and was served.

Other file types tested:
- `/ftp/package.json.bak` → 403 "Only .md and .pdf files are allowed!"
- `/ftp/encrypt.pyc` → 403 "Only .md and .pdf files are allowed!"
- `/ftp/suspicious_errors.yml` → 403 "Only .md and .pdf files are allowed!"

## Impact
The KeePass database likely contains stored credentials (passwords, API keys, etc.). An attacker can download this file and attempt to crack it offline if a weak master password is used.

## Risk
High — KeePass database may contain credentials. Additionally, the file extension filter was bypassed.