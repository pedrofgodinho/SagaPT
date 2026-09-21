## Sensitive File Exposure — Large Encrypted Announcement File

- **Endpoint:** GET http://juiceshop.local:3000/ftp/announcement_encrypted.md
- **Vulnerability Class:** Sensitive Information Exposure
- **Evidence:** Returns HTTP 200 with `Content-Type: text/markdown` and Content-Length: 369,237 bytes. The file contains a large body of numeric data (appears to be encrypted/encoded content). The file name suggests it is an encrypted announcement, potentially containing sensitive business information.
- **Impact:** Large encrypted/sensitive files are publicly accessible via the `/ftp/` directory.
- **Priority:** MEDIUM — file is accessible but content appears encrypted/encoded.