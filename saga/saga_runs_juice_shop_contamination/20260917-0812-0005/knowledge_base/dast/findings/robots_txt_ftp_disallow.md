## Robots.txt Disallows FTP Directory

**Endpoint:** GET /robots.txt
**Vulnerability Class:** Information Disclosure

### Evidence
```
User-agent: *
Disallow: /ftp
```

### Analysis
The robots.txt file explicitly disallows crawling of the /ftp/ directory, which ironically draws attention to it. This is a common pattern in vulnerable applications where the developer attempts to hide sensitive files but the disallow directive actually guides attackers to them.

The /ftp/ directory contains:
- Confidential acquisition plans (acquisitions.md)
- KeePass database (incident-support.kdbx)
- Encrypted announcement (369KB)
- Malware quarantine shortcuts

### Impact
The robots.txt file inadvertently guides attackers to the sensitive /ftp/ directory.