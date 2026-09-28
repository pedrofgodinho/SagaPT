# Web3 API Endpoints Discovered in JavaScript Bundle

## Vulnerability Class
Information Disclosure / Undocumented API Endpoints

## Endpoint
Multiple web3 endpoints discovered in `main.js` JavaScript bundle:
- `GET /rest/web3/nftUnlocked`
- `GET /rest/web3/nftMintListen`
- `POST /rest/web3/submitKey`
- `POST /rest/web3/walletNFTVerify`
- `POST /rest/web3/walletExploitAddress`
- `GET /api/Challenges/` (with query parameter filtering)
- `GET /api/Challenges/?key=<challenge_key>`

## Detection Evidence
The `main.js` bundle (1.2MB) contains Angular service classes that define these endpoints:

From `init_chunk_K7PQ47BU` (Web3Service):
```javascript
hostServer = L$.hostServer;
host = this.hostServer + '/rest/web3';
nftUnlocked() { return this.http.get(this.host + '/nftUnlocked') }
nftMintListen() { return this.http.get(this.host + '/nftMintListen') }
submitKey(t) { return this.http.post(this.host + '/submitKey', {privateKey: t}) }
verifyNFTWallet(t) { return this.http.post(this.host + '/walletNFTVerify', {walletAddress: t}) }
walletAddressSend(t) { return this.http.post(this.host + '/walletExploitAddress', {walletAddress: t}) }
```

From `init_chunk_S$1` (FeedbacksService):
```javascript
host = this.hostServer + '/api/Feedbacks';
find(a) { return this.http.get(this.host + '/', {params: a}) }
save(a) { return this.http.post(this.host + '/', a) }
del(a) { return this.http.delete(this.host + '/' + a) }
```

## Evidence
- `GET /api/Challenges/` returns all 30+ challenge definitions including descriptions, difficulty ratings, and categories
- `GET /api/Challenges/?key=nftMintChallenge` returns filtered challenge details
- `GET /api/Feedbacks/` returns publicly accessible feedback data with UserIDs

## Impact
- Web3 endpoints expose NFT/wallet interaction APIs that could be targeted
- Challenge endpoint reveals all security challenges including their descriptions and difficulty
- Feedbacks endpoint exposes user data publicly
- These endpoints are discoverable through static analysis of client-side JavaScript

## Risk
**Medium** — Undocumented API endpoints that may lack proper security controls. Challenge descriptions may aid targeted attacks.

## Notes
- These endpoints are not listed in the recon attack surface documentation
- The web3 endpoints handle cryptocurrency wallet interactions
- Challenge filtering via query parameter (`?key=`) is functional