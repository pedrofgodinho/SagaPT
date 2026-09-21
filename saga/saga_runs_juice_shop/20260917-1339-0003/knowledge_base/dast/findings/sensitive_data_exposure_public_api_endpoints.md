## Sensitive Data Exposure via Public API Endpoints

**Endpoints:** GET /api/Challenges/, GET /api/Feedbacks/
**Vulnerability Class:** Excessive Data Exposure / Information Disclosure

### Evidence

1. **GET /api/Challenges/** returns ALL challenge details publicly:
   - HTTP 200 with full JSON body containing 67,660 bytes of data
   - Exposes: challenge names, keys, categories, descriptions, difficulty ratings, tags, coding challenge status, creation/update timestamps, and challenge dependencies
   - Includes sensitive challenge metadata such as:
     - `passwordHashLeakChallenge`: "Obtain the password (hash) of the currently logged-in user directly from a REST API endpoint"
     - `adminSectionChallenge`: "Access the administration section of the store"
     - `accessLogDisclosureChallenge`: "Gain access to any access log file of the server"
     - `fileWriteChallenge`: "Overwrite the Legal Information file"
     - `rceChallenge`: "Perform a Remote Code Execution..."
     - `web3WalletChallenge`: "Withdraw more ETH from the new wallet..."
     - Alchemy API documentation URLs and configuration details

2. **GET /api/Feedbacks/** returns user feedback with UserIds and partial emails:
   - HTTP 200 with 8 feedback entries
   - Exposes: UserId (1, 2, 3, 21, null), comment text, ratings, timestamps
   - Contains a seed phrase in feedback #4: `"purpose betray marriage blame crunch monitor spin slide donate sport lift clutch"`
   - Contains an embedded XSS payload in feedback #5: `<br /><em>Support Team: ...</em>`

3. **Login response** (POST /rest/user/login) returns password hash:
   - JWT payload contains `"password": "0192023a7bbd73250516f069df18b500"` (SHA1 hash of admin password)

### Impact
Attackers can enumerate all application challenges, their categories, and difficulty levels. The exposed seed phrase in feedback data could be used for wallet recovery. The password hash leak enables offline cracking.

### Notes
These endpoints do not require authentication. The /api/Challenges/ endpoint exposes the application's challenge map to potential attackers.