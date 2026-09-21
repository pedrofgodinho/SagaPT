# Sensitive File Exposure: Confidential Acquisitions Document

## Vulnerability Class
Sensitive File Exposure / Information Disclosure

## Endpoint
`GET /ftp/acquisitions.md`

## Evidence
- **HTTP Status**: 200 OK
- **Content-Type**: `text/markdown; charset=UTF-8`
- **Content-Length**: 909 bytes
- Document is explicitly marked: "This document is confidential! Do not distribute!"
- Content reveals planned company acquisitions of competitors
- States: "Our company plans to acquire several competitors within the next year. This will have a significant stock market impact..."

## Impact
Confidential business information (planned mergers/acquisitions) is publicly accessible. This could be used for:
- Insider trading (if the information affects stock prices)
- Competitive intelligence gathering
- Social engineering attacks against the company or its partners

## Detection Payload
`GET /ftp/acquisitions.md` → Returns confidential document content