# Stored XSS in Feedbacks Endpoint

- **Endpoint:** GET /api/Feedbacks
- **Vulnerable Parameter:** `comment` field in user-submitted feedback
- **Evidence:** The unauthenticated /api/Feedbacks endpoint returns feedback comments containing unescaped HTML:
  - Feedback ID 5: `"comment":"Incompetent customer support! Can't even upload photo of broken purchase!<br /><em>Support Team: Sorry, only order confirmation PDFs can be attached to complaints!</em>"`
  - Feedback ID 6: `"comment":"This is <b>the</b> store for awesome stuff of all kinds!"`
  - Feedback ID 4 contains a wallet seed phrase: `"purpose betray marriage blame crunch monitor spin slide donate sport lift clutch"`
- **Impact:** User-submitted comments containing HTML tags are stored and reflected back unescaped to all viewers. An attacker can craft feedback with arbitrary HTML/JavaScript to execute in other users' browsers.
- **Risk:** High - Stored XSS affects all users viewing feedback, combined with wallet seed phrase exposure