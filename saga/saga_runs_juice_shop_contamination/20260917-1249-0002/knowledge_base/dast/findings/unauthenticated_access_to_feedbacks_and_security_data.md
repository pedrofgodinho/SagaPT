# Unauthenticated Access to Sensitive API Endpoints

- **Endpoints:** GET /api/Feedbacks, GET /api/Challenges, GET /api/SecurityQuestions
- **Detection Payload:** GET requests to all three endpoints without authentication
- **Evidence:** 
  - /api/Feedbacks returns 200 with all feedback entries including user IDs, comments with partially masked emails, ratings, and timestamps. Contains wallet recovery seed phrase: "purpose betray marriage blame crunch monitor spin slide donate sport lift clutch"
  - /api/Challenges returns 200 with all challenge definitions
  - /api/SecurityQuestions returns 200 with all 14 security questions and their IDs
- **Impact:** Sensitive data exposed without authentication. Wallet recovery phrases, security questions (useful for account takeover), and challenge data are publicly accessible.
- **Risk:** High - Contains wallet recovery seed phrase and security questions