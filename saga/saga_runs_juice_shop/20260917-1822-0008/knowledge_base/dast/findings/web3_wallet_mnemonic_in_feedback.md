## Cryptocurrency Wallet Mnemonic Phrase Exposed in Feedback Data

- **Endpoint:** GET http://juiceshop.local:3000/api/Feedbacks
- **Vulnerability Class:** Sensitive Data Exposure
- **Detection Payload:** GET /api/Feedbacks (unauthenticated)
- **Evidence:** Feedback entry with id=4, UserId=21 contains a comment with a 12-word Ethereum wallet mnemonic phrase:
  `"purpose betray marriage blame crunch monitor spin slide donate sport lift clutch"`
  This is a BIP39 seed phrase that can be used to derive private keys and access the associated wallet.
- **Impact:** Attacker can use this mnemonic phrase to recover the wallet's private key and access any funds or NFTs in the wallet. This represents a real cryptocurrency loss vector.
- **Priority:** CRITICAL - direct cryptocurrency wallet compromise.