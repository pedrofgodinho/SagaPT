## FTP Extension Filter Blocks Non-Markdown/PDF Files

**Endpoint:** GET /ftp/
**Vulnerability Class:** Path Traversal / File Inclusion (blocked)

### Tests Performed
- `GET /ftp/suspicious_errors.yml` → 403 "Error: Only .md and .pdf files are allowed!"
- `GET /ftp/acquisitions.md` → 200, markdown content served (no executable content)

### Evidence
The FTP file server enforces an extension whitelist allowing only `.md` and `.pdf` files. Attempts to access files with other extensions return 403 with the error message "Error: Only .md and .pdf files are allowed!" The served markdown files contain static text content with no executable or reflective content.

### Conclusion
No XSS vulnerability confirmed via FTP file inclusion. The extension filter prevents uploading or accessing arbitrary file types. Markdown files served via FTP contain only static text content.