# Sensitive Data Leakage in /api/Feedbacks/ API

## Vulnerability Class
Information Disclosure / Sensitive Data Exposure

## Endpoint
`GET /api/Feedbacks/` (public, no authentication required)

## Evidence
The endpoint returns 8 feedback records containing:
- **User IDs** (UserId field): 1, 2, 3, 21 linked to specific feedback
- **Partial email addresses** embedded in comment text: "***in@juice-sh.op", "***@juice-sh.op", "***der@juice-sh.op", "***ereum@juice-sh.op"
- **Wallet mnemonic phrase** (12-word BIP39 seed) in feedback ID 4: `purpose betray marriage blame crunch monitor spin slide donate sport lift clutch`
- **Wallet address reference** in comment: "/juicy-nft"
- **Full timestamps** (createdAt, updatedAt) for each record
- **Internal support communications** exposed in comments (e.g., "Support Team: Sorry, only order confirmation PDFs can be attached to complaints!")
- **Anonymous vs registered user distinction** via UserId null/not-null

## Detection Payload
```
GET /api/Feedbacks/
Authorization: (none)
```

## Response Sample
```json
{
  "UserId": 21,
  "id": 4,
  "comment": "Please send me the juicy chatbot NFT in my wallet at /juicy-nft : \"purpose betray marriage blame crunch monitor spin slide donate sport lift clutch\" (**ereum@juice-sh.op)",
  "rating": 1
}
```

## Impact
- **CRITICAL**: 12-word BIP39 wallet mnemonic phrase exposed publicly. This seed phrase can be used to derive all private keys for the associated wallet and steal any funds.
- **HIGH**: User IDs and partial email addresses enable user enumeration and targeted attacks.
- **MEDIUM**: Internal support communications reveal operational procedures.

## Risk
**Critical** — Cryptographic seed material exposed in publicly accessible API.