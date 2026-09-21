# Sensitive File Exposure: KeePass Database

## Vulnerability Class
Sensitive File Exposure / Information Disclosure

## Endpoint
`GET /ftp/incident-support.kdbx`

## Evidence
- **HTTP Status**: 200 OK
- **Content-Type**: `application/octet-stream`
- **Content-Length**: 3246 bytes (binary data)
- The file is a KeePass database (`.kdbx`) containing encrypted credentials/security data
- No authentication or authorization required to access
- Extension filter (`Only .md and .pdf files are allowed`) does NOT block `.kdbx` files

## Impact
A KeePass database may contain stored passwords, encryption keys, or other credentials for the application infrastructure. If the database password is weak or known, an attacker could extract all stored credentials.

## Detection Payload
`GET /ftp/incident-support.kdbx`

## Notes
- The `.kdbx` file bypasses the file extension filter that blocks `.bak`, `.pyc`, `.yml`, `.gg` files
- Other sensitive files (`.bak`, `.pyc`) are blocked by the extension filter