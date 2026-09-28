## FTP Directory Exposes Sensitive and Confidential Files

**Endpoint:** GET /ftp/* (directory listing and file access)
**Vulnerability Class:** Sensitive Information Exposure

### Detection

The `/ftp/` directory is publicly accessible and contains multiple sensitive files including confidential business documents, encrypted data files, KeePass password databases, and malware samples. While `robots.txt` disallows `/ftp`, this is advisory only and not enforced.

### Sensitive Files Accessed

1. **`/ftp/acquisitions.md`** (909 bytes, HTTP 200)
   - Content: Confidential acquisition plans with statement "This document is confidential! Do not distribute!"
   - Contains business-sensitive information about planned competitor acquisitions

2. **`/ftp/incident-support.kdbx`** (3,246 bytes, HTTP 200)
   - Content: KeePass database file containing potentially stored credentials
   - Binary format, publicly downloadable

3. **`/ftp/legal.md`** (3,047 bytes, HTTP 200)
   - Content: Legal terms and conditions document

4. **`/ftp/announcement_encrypted.md`** (369,237 bytes, HTTP 200)
   - Content: Large encrypted announcement file containing 100+ digit numbers (possibly RSA-encrypted data or encoded secrets)

5. **`/ftp/quarantine/juicy_malware_windows_64.exe.url`** (168 bytes, HTTP 200)
   - Content: Windows Internet Shortcut pointing to `https://github.com/juice-shop/juicy-malware/raw/master/juicy_malware_windows_64.exe`
   - Points to external malware distribution

### File Access Controls

- Only `.md` and `.pdf` files are explicitly allowed by the file server (`/ftp/package.json.bak` returns 403 with "Only .md and .pdf files are allowed!")
- However, `.kdbx` files ARE accessible (incident-support.kdbx returned 200)
- Directory listing of `/ftp/` is accessible

### Evidence

Request: `GET /ftp/acquisitions.md`
Response: HTTP 200 with body containing confidential acquisition plans

Request: `GET /ftp/incident-support.kdbx`
Response: HTTP 200 with binary KeePass database content (3,246 bytes)

Request: `GET /ftp/quarantine/juicy_malware_windows_64.exe.url`
Response: HTTP 200 with Internet Shortcut pointing to malware URL

### Impact

- Confidential business information (acquisition plans) is publicly accessible
- KeePass database may contain stored credentials/passwords
- Encrypted announcement may contain encoded secrets or keys
- Malware URLs are accessible, potentially facilitating social engineering attacks
- robots.txt is advisory only and does not prevent access

### Recommendation

- Restrict access to the `/ftp/` directory with authentication
- Remove or relocate confidential documents from publicly accessible paths
- Block access to `.kdbx` and other sensitive file types
- Implement proper access controls rather than relying on robots.txt