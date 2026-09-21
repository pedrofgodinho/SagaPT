## Cryptocurrency Seed Phrase Exposure in Public Feedback API

**Endpoint:** GET /api/Feedbacks/
**Vulnerability Class:** Sensitive Data Exposure

### Evidence

The public /api/Feedbacks/ endpoint (HTTP 200, no authentication required) returns feedback entry #4 which contains a 12-word BIP39 cryptocurrency seed phrase:

```
"purpose betray marriage blame crunch monitor spin slide donate sport lift clutch"
```

Full feedback entry:
```json
{
  "UserId": 21,
  "id": 4,
  "comment": "Please send me the juicy chatbot NFT in my wallet at /juicy-nft : \"purpose betray marriage blame crunch monitor spin slide donate sport lift clutch\"",
  "rating": 1,
  "createdAt": "2026-09-17T13:38:58.732Z",
  "updatedAt": "2026-09-17T13:38:58.732Z"
}
```

The comment references `/juicy-nft` (a Web3 challenge endpoint) and the seed phrase is a standard 12-word BIP39 mnemonic.

### Impact
This seed phrase can be used to:
1. Recover the associated cryptocurrency wallet using any BIP39-compatible wallet tool
2. Access any funds stored in that wallet
3. Potentially access the NFT referenced in the comment

### Notes
This appears to be a challenge-related seed phrase for the NFTTakeover challenge, but it is exposed in a publicly accessible API endpoint. In a real application, such credentials should never be stored in user-generated content accessible via public APIs.