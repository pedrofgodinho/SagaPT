# Cross-Origin Resource Sharing (CORS) Wildcard

**Endpoints:** All tested endpoints
**Vulnerable Parameter:** N/A (response header)
**Vulnerability Class:** Cross-Domain Misconfiguration

## Evidence
Every endpoint tested returns the following CORS header:
```
Access-Control-Allow-Origin: *
```

This was observed on:
- `GET /rest/web3/nftUnlocked`
- `GET /rest/web3/nftMintListen`
- `POST /rest/web3/submitKey`
- `POST /rest/web3/walletNFTVerify`
- `POST /rest/web3/walletExploitAddress`
- `GET /ftp/`
- `GET /ftp/acquisitions.md`
- `GET /ftp/announcement_encrypted.md`
- `GET /ftp/encrypt.pyc`
- `GET /ftp/incident-support.kdbx`
- `GET /ftp/quarantine/`
- `GET /#/jobs`
- `GET /#/forgot-password`
- `GET /api/Products`
- `GET /api/Products/{id}`
- `GET /api/SecurityQuestions`
- `POST /api/Users`

## Detection
```
GET /rest/web3/nftUnlocked
Response Header: Access-Control-Allow-Origin: *
```

## Impact
- Any website can make cross-origin requests to this application
- Combined with authenticated endpoints, this could enable CSRF attacks
- Attackers could potentially exfiltrate data via cross-origin requests
- Sensitive data accessible from malicious third-party sites

## Notes
ZAP flagged this as a Medium risk "Cross-Domain Misconfiguration" on multiple endpoints.