## Broken /redirect Endpoint with Application Error Disclosure

**Endpoint:** GET /redirect?url=<any_value>
**Vulnerability Class:** Application Error Disclosure (Stack Trace)

### Detection

The `/redirect` endpoint is broken and returns HTTP 500 with a full stack trace for ALL requests, regardless of the `url` parameter value. Tested payloads:
- `GET /redirect?url=http://juiceshop.local:3000` (valid URL)
- `GET /redirect?url=http://evil.com` (external URL)
- `GET /redirect?url=//evil.com` (protocol-relative)
- `GET /redirect?target=http://evil.com` (different param name)
- `GET /redirect?destination=http://evil.com` (different param name)

All returned:
```
HTTP 500
TypeError: Cannot read properties of undefined (reading 'includes')
```

Stack trace points to:
```
at Object.isRedirectAllowed (/juice-shop/build/lib/insecurity.js:157:34)
at /juice-shop/build/routes/redirect.js:47:22
```

### Evidence

The `isRedirectAllowed` function in `insecurity.js:157` attempts to call `.includes()` on an undefined value, suggesting the `url` query parameter is not being properly read from the request. This is likely a bug where the redirect route expects a different parameter name or the query string parsing fails.

### Impact

- Full stack trace reveals application internals: file paths (`/juice-shop/build/lib/insecurity.js`, `/juice-shop/build/routes/redirect.js`)
- Confirms the application has a redirect route that is currently non-functional
- The error suggests the redirect allowlist logic is broken

### Recommendation

Fix the redirect route to properly parse the URL parameter and implement a proper allowlist-based redirect mechanism. Ensure stack traces are suppressed in production responses.