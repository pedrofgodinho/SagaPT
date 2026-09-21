# Web3 SubmitKey Endpoint Discovered

## Vulnerability Class
Information Disclosure / Undocumented API Endpoint

## Endpoint
`POST /rest/web3/submitKey`

## Evidence
- POST to `/rest/web3/submitKey` with `{"privateKey":"test123"}` returns:
  ```json
  {"success":false,"message":"Looks like you entered a non-Ethereum private key to access me.","status":{"id":9,"key":"nftUnlockChallenge","name":"NFT Takeover",...}}
  ```
- Response includes the challenge object with full metadata (id, key, name, category, difficulty, description)

## Impact
The endpoint reveals challenge metadata including the challenge key (`nftUnlockChallenge`), difficulty level, and full description. This information could help attackers focus on solving specific Web3 challenges.

## Risk
Low — Information disclosure through undocumented endpoint.