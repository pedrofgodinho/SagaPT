## CORS - No Credentials Access-Control-Allow-Credentials Header

**Endpoint:** All endpoints (/, /rest/user/login, /api/Feedbacks/, /rest/web3/*, /ftp/*)
**Vulnerability Class:** Cross-Origin Resource Sharing (CORS) Misconfiguration (partial)

### Evidence
All endpoints return `Access-Control-Allow-Origin: *` but do NOT return `Access-Control-Allow-Credentials: true`.

Example response headers from GET /:
```
Access-Control-Allow-Origin: *
# Note: NO Access-Control-Allow-Credentials header present
```

### Impact
While `Access-Control-Allow-Origin: *` is present on all endpoints, the absence of `Access-Control-Allow-Credentials: true` means that browsers will NOT send cookies or HTTP authentication headers in cross-origin requests. This significantly limits the ability of an attacker to perform cross-origin data theft using credentials.

However, the CORS misconfiguration still allows:
- Cross-origin read of non-sensitive public data (e.g., FTP files, product listings)
- Cross-origin POST requests without credentials (which could be used for CSRF-like attacks if the target endpoint doesn't require authentication)
- Potential abuse with custom headers or API keys passed in request body

### Combined Risk
This CORS misconfiguration combined with the missing CSRF protection on /rest/user/login (confirmed separately) means that any cross-origin POST to the login endpoint would not carry session cookies, reducing but not eliminating the risk.

### Remediation
1. Remove the wildcard `*` and implement an allowlist of trusted origins
2. If credentials are needed, set `Access-Control-Allow-Credentials: true` AND restrict origins to specific domains (never combine `*` with credentials)