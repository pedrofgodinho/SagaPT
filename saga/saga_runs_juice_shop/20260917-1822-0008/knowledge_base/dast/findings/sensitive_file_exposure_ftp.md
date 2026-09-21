## Sensitive File Exposure via FTP Directory

- **Endpoint:** GET http://juiceshop.local:3000/ftp/
- **Vulnerability Class:** Sensitive Information Exposure
- **Evidence:** 
  1. `/ftp/` returns 200 with a browsable directory listing showing all files
  2. `/ftp/incident-support.kdbx` returns 200 with `Content-Type: application/octet-stream` (3246 bytes) — this is a KeePass password database file containing credentials
  3. `/ftp/acquisitions.md` returns 200 with `Content-Type: text/markdown` — contains confidential M&A information: "Our company plans to acquire several competitors within the next year. This will have a significant stock market impact..."
  4. Directory listing also reveals: `announcement_encrypted.md`, `coupons_2013.md.bak`, `eastere.gg`, `encrypt.pyc`, and `quarantine/` subdirectory
- **Impact:** Confidential business documents and credential databases are publicly accessible without authentication.
- **Priority:** HIGH