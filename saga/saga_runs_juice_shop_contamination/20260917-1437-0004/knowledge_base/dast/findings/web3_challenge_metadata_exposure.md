# Web3 Challenge Metadata Exposure

**Endpoints:**
- `POST /rest/web3/submitKey`
- `POST /rest/web3/walletNFTVerify`
- `GET /rest/web3/nftUnlocked`
- `GET /rest/web3/nftMintListen`
- `POST /rest/web3/walletExploitAddress`

**Vulnerability Class:** Sensitive Information Disclosure

## Evidence
All Web3 endpoints return full challenge metadata in their JSON responses, including:
- Challenge ID and key name
- Challenge name and category
- Full description text
- Difficulty rating
- Tags (e.g., "Web3", "Coding Challenge")
- Whether it has a coding challenge
- Creation and update timestamps

**Example from `POST /rest/web3/submitKey` (401 response):**
```json
{
  "success": false,
  "message": "Looks like you entered a non-Ethereum private key to access me.",
  "status": {
    "id": 9,
    "key": "nftUnlockChallenge",
    "name": "NFT Takeover",
    "category": "Sensitive Data Exposure",
    "tags": "Contraption,Good for Demos,Web3,With Coding Challenge",
    "description": "Take over the wallet containing our official Soul Bound Token (NFT).",
    "difficulty": 2,
    "solved": false,
    "hasCodingChallenge": true,
    "createdAt": "2026-09-17T14:37:53.881Z",
    "updatedAt": "2026-09-17T14:37:53.881Z"
  }
}
```

## Detection
```
POST /rest/web3/submitKey
Body: {"key": "test"}
Response: 401 with full challenge metadata in "status" field
```

## Impact
- Attackers can enumerate all Web3 challenges without solving them
- Full challenge descriptions reveal the nature of the exploit needed
- Difficulty ratings help prioritize attack efforts
- Tags help identify challenge categories for targeted attacks
- Timestamps reveal when challenges were created/modified

## Notes
This metadata is returned even on 401 (unauthorized) responses, meaning no authentication is required to discover all challenge details.