## Information Disclosure - API Feedbacks Endpoint Returns All User Feedback

- **Endpoint:** GET /api/Feedbacks
- **Auth Required:** No (publicly accessible)
- **Evidence:** Returns 200 OK with JSON containing all feedback entries including:
  - User IDs (UserId field)
  - Comment text (some containing HTML)
  - Ratings
  - Created/updated timestamps
  - Partially masked email addresses (e.g., "***in@juice-sh.op", "***@juice-sh.op", "***der@juice-sh.op", "***ereum@juice-sh.op")

- **Notable Data Exposed:**
  - Feedback from user with ID 21 contains a seed phrase: "purpose betray marriage blame crunch monitor spin slide donate sport lift clutch" (NFT wallet recovery phrase)
  - Anonymous feedback contains embedded HTML (potential stored XSS vector)

- **Impact:** User PII exposure through partially masked emails, correlation with other data sources, and exposure of sensitive wallet recovery phrases in user feedback.

- **Risk:** High - Contains wallet recovery seed phrase in user-generated content