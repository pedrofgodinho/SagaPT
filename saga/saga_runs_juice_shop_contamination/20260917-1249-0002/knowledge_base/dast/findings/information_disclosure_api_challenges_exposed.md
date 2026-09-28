## Information Disclosure - API Challenges Endpoint Exposes All CTF Challenges

- **Endpoint:** GET /api/Challenges
- **Auth Required:** No (publicly accessible)
- **Evidence:** Returns 200 OK with full JSON containing all challenge definitions (67,663 bytes). Response includes:
  - Challenge IDs, keys, names, categories, descriptions
  - Difficulty ratings (1-6)
  - Tags (e.g., "Danger Zone", "Web3", "OSINT")
  - Mitigation URLs pointing to OWASP cheat sheets
  - ChallengeDependencies (revealing prerequisite chains)
  - Coding challenge status flags

- **Sample Data Exposed:**
  - "Password Hash Leak" - "Obtain the password (hash) of the currently logged-in user directly from a REST API endpoint."
  - "API-only XSS" - "Perform a persisted XSS attack... without using the frontend application at all"
  - "Admin Registration" - "Register as a user with administrator privileges"
  - "Admin Section" - "Access the administration section of the store"
  - "Blockchain Hype" - "Learn about the Token Sale before its official announcement"
  - "Wallet Depletion" - "Withdraw more ETH from the new wallet than you deposited"
  - "Christmas Special" - "Order the Christmas special offer of 2014" (category: Injection)

- **Impact:** Attackers gain complete knowledge of all application security challenges, their categories, difficulty levels, and descriptions. This enables targeted attacks against specific security controls and reveals the application's security architecture.

- **Risk:** High - Provides attackers with a complete roadmap of security challenges