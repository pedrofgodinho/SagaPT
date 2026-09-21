## Information Disclosure - Confidential Files Accessible via /ftp/

- **Endpoint:** GET /ftp/acquisitions.md
- **Evidence:** The file returned 200 OK with content-type `text/markdown` containing confidential business information:
  ```
  # Planned Acquisitions
  > This document is confidential! Do not distribute!
  Our company plans to acquire several competitors within the next year.
  This will have a significant stock market impact...
  ```
- **Additional Files Exposed:**
  - `/ftp/legal.md` - Legal information / Terms of Use
  - `/ftp/incident-support.kdbx` - KeePass password database (3246 bytes)
  - `/ftp/announcement_encrypted.md` - Large encrypted announcement (369KB)
  - `/ftp/eastere.gg` - Easter egg file
  - `/ftp/encrypt.pyc` - Python bytecode file
  - `/ftp/quarantine/` - Directory with malware URL files
- **Impact:** Confidential business documents, password databases, and other sensitive files are publicly accessible via the /ftp/ directory.
- **Risk:** High
