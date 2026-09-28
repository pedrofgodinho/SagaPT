# Unauthenticated Access to Feedback List

## Vulnerability Class
Broken Access Control — Information Disclosure

## Endpoint
`GET /api/Feedbacks/`

## Description
The feedback list endpoint returns all user feedback entries without requiring authentication. This includes feedback from other users with their UserIds, ratings, and comments. While individual feedback items (`GET /api/Feedbacks/{id}`) require authentication (401), the list endpoint is publicly accessible.

## Detection Payload
- `GET /api/Feedbacks/` → HTTP 200 with full list of feedback entries

## Evidence
The endpoint returned HTTP 200 with the following data:
```json
{
  "status": "success",
  "data": [
    {"UserId":1, "id":1, "comment":"I love this shop!...", "rating":5},
    {"UserId":2, "id":2, "comment":"Great shop!...", "rating":4},
    {"UserId":3, "id":3, "comment":"Nothing useful...", "rating":1},
    {"UserId":21, "id":4, "comment":"Please send me the juicy chatbot NFT...", "rating":1},
    {"UserId":null, "id":5, "comment":"Incompetent customer support!...", "rating":2},
    {"UserId":null, "id":6, "comment":"This is the store...", "rating":4},
    {"UserId":null, "id":7, "comment":"Never gonna buy anywhere...", "rating":4},
    {"UserId":null, "id":8, "comment":"Keep up the good work!...", "rating":3}
  ]
}
```

## Impact
An unauthenticated attacker can enumerate all customer feedback entries, including UserIds associated with each feedback, ratings, and comments. This could be used for user enumeration, social engineering, or building a profile of active users.

## Mitigation
- Require authentication for the feedback list endpoint
- If public feedback display is needed, mask or hash UserIds