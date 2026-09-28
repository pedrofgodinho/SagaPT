## Sensitive Files Exposed via /ftp/ Directory

**Endpoint:** `GET http://juiceshop.local:3000/ftp/`
**Vulnerability Class:** Information Disclosure

### Testing Performed
- Directory listing: `/ftp/` → 200 with listing
- File access: `/ftp/acquisitions.md` → 200 with confidential content
- File access: `/ftp/legal.md` → 200
- File access: `/ftp/incident-support.kdbx` → 200 with binary data (3246 bytes)

### Evidence
- The `/ftp/` directory is publicly accessible and returns a directory listing.
- `/ftp/acquisitions.md` contains confidential acquisition plans marked "Do not distribute!"
- `/ftp/incident-support.kdbx` is a KeePass database file accessible without restriction.

### Analysis
The /ftp/ directory exposes sensitive files including confidential business documents and a KeePass database file. The file type restriction (.md/.pdf only) has an edge case allowing `.kdbx` files.

### Impact
Information disclosure of confidential business documents and potentially sensitive credential data.