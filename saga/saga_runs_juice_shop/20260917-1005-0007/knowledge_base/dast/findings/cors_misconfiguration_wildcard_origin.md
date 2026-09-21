# CORS Misconfiguration: Wildcard Access-Control-Allow-Origin

## Vulnerability Class
CORS Misconfiguration / Security Misconfiguration

## Endpoint
All endpoints, verified on:
- `GET /` (home page)
- `GET /ftp/acquisitions.md`
- `GET /ftp/incident-support.kdbx`
- `GET /ftp/`
- `GET /robots.txt`
- `GET /styles.css`

## Evidence
All tested responses include the header:
`Access-Control-Allow-Origin: *`

This wildcard value allows any origin to make cross-origin requests to the application, including malicious third-party sites.

## Impact
An attacker can craft cross-origin requests from any domain to:
- Read sensitive data served by the application (e.g., acquisitions.md, incident-support.kdbx)
- Perform actions on behalf of authenticated users (if cookies are sent with cross-origin requests)
- Bypass browser same-origin policy protections

## Detection
Checked response headers on multiple endpoints - all include `Access-Control-Allow-Origin: *`