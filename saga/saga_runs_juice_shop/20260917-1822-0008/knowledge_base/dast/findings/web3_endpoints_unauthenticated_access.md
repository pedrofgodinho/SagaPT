## Web3 Endpoints Accessible Without Authentication

- **Endpoints:**
  - GET http://juiceshop.local:3000/rest/web3/nftUnlocked → `{"status":false}`
  - GET http://juiceshop.local:3000/rest/web3/nftMintListen → `{"success":true,"message":"Event Listener Created"}`
  - POST http://juiceshop.local:3000/rest/web3/submitKey → `{"success":false,"message":"Looks like you entered a non-Ethereum private key..."}`
  - POST http://juiceshop.local:3000/rest/web3/walletNFTVerify → `{"success":false,"message":"Wallet did not mint the NFT"}`
  - POST http://juiceshop.local:3000/rest/web3/walletExploitAddress → `{"success":true,"message":"Event Listener Created"}`
- **Vulnerability Class:** Broken Access Control
- **Detection Payload:** Unauthenticated GET/POST to all Web3 endpoints
- **Evidence:** All five Web3 endpoints return functional responses without authentication. The submitKey endpoint accepts any private key string and responds with validation feedback. The walletNFTVerify and walletExploitAddress endpoints accept wallet addresses and return NFT verification status.
- **Impact:** Web3 endpoints are publicly accessible and interactive. An attacker can probe wallet verification logic, submit arbitrary keys, and interact with the NFT minting/verification system without authentication. The submitKey endpoint specifically allows testing arbitrary private keys against the wallet verification flow.
- **Priority:** MEDIUM - Web3 endpoints are interactive and accept arbitrary input without auth, though they don't directly expose sensitive data.