# Stored XSS in Feedbacks Comments

## Vulnerability Class
Stored Cross-Site Scripting (XSS)

## Endpoint
`GET /api/Feedbacks/`

## Vulnerable Parameter
`comment` field in feedback data

## Detection Evidence
The GET `/api/Feedbacks/` endpoint returns stored user comments that contain unescaped HTML tags:

- Feedback ID 5 contains: `<br /><em>Support Team: Sorry, only order confirmation PDFs can be attached to complaints!</em>`
- Feedback ID 6 contains: `<b>the</b>`
- Feedback ID 21 contains wallet mnemonic phrase in comment text

## Evidence
```json
{
  "UserId": null,
  "id": 5,
  "comment": "Incompetent customer support! Can't even upload photo of broken purchase!<br /><em>Support Team: Sorry, only order confirmation PDFs can be attached to complaints!</em>",
  "rating": 2
}
```

```json
{
  "UserId": null,
  "id": 6,
  "comment": "This is <b>the</b> store for awesome stuff of all kinds!",
  "rating": 4
}
```

## Impact
HTML tags stored in comments are returned unescaped in the JSON API response. If the frontend SPA renders these values as HTML (rather than text), stored XSS payloads could execute in the context of any user viewing the feedbacks.

## Risk
**Medium** — Stored XSS in publicly accessible endpoint. Depends on frontend rendering behavior.

## Notes
- The endpoint is publicly accessible (no authentication required)
- Comments are stored with HTML tags that are not sanitized on input
- The response Content-Type is application/json, but Angular SPAs may render innerHTML