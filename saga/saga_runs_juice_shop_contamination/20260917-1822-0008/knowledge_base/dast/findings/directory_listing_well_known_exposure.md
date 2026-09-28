## Vulnerability: Directory Listing Exposure on .well-known/

**Endpoint:** `/.well-known/`
**Parameter:** N/A (path-based)
**Vulnerability Class:** Information Disclosure

### Description
The `.well-known/` directory is accessible and returns a directory listing showing:
- `security.txt` file (73 bytes) - contains security contact information
- `csaf/` directory - contains CSAF (Common Security Advisory Framework) data

### Evidence
```
GET /.well-known/ → HTTP 200
Directory listing shows: security.txt, csaf/
```

### security.txt Content:
- Contact email: `mailto:donotreply@owasp-juice.shop`
- PGP encryption key URL
- CSF provider metadata URL: `http://localhost:3000/.well-known/csaf/provider-metadata.json`
- Hiring page link
- Expiration date

### Impact
Exposes security contact information and potentially sensitive CSAF security advisories that could reveal known vulnerabilities.

### Risk
Low - Information disclosure of security contact and advisory data.