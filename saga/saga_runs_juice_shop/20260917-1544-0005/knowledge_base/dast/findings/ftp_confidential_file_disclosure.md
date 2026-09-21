## FTP File Server - Confidential Document Disclosure

**Vulnerability Class:** Information Disclosure
**Endpoint:** GET /ftp/acquisitions.md
**Evidence:**
- Request: GET http://juiceshop.local:3000/ftp/acquisitions.md (unauthenticated)
- Response: HTTP 200 with full document content
- Document header states: "This document is confidential! Do not distribute!"
- Content describes "planned acquisitions" of competitors "within the next year" with "significant stock market impact"
- File size: 909 bytes
- The document is publicly accessible without any authentication

Other confidential FTP files also accessible:
- /ftp/legal.md (3047 bytes) - Legal information with Terms of Use
- /ftp/announcement_encrypted.md (369KB) - Large file containing numeric data

**Impact:** Confidential business documents are publicly accessible. The acquisitions document could be used for insider trading or competitive intelligence.

**Detection Payload:** GET /ftp/acquisitions.md (unauthenticated)