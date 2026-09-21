## Application Error Disclosure on Unregistered Endpoints

**Affected Endpoints:** Multiple unregistered paths including:
- POST /rest/user/registration
- POST /rest/user/register
- POST /api/user/register
- POST /rest/user/signup
- POST /api/user/signup
- POST /api/auth/signup
- POST /rest/auth/signup
- POST /api/Feedback
- POST /api/Complaint
- GET /api/Feedbacks (requires captchaId)
- GET /api/Complaints (requires auth)

**Vulnerability Class:** Application Error Disclosure

### Evidence
All unregistered endpoints returned HTTP 500 with detailed error pages including:
- Full application name: "OWASP Juice Shop (Express ^4.22.1)"
- Stack traces showing file paths (e.g., `/juice-shop/build/routes/angular.js:18:18`)
- For /api/Feedbacks: "WHERE parameter \"captchaId\" has invalid \"undefined\" value" with Sequelize query generator stack trace
- For /api/Complaints: "UnauthorizedError: No Authorization header was found"

### Impact
- Reveals technology stack (Express ^4.22.1, Sequelize ORM, SQLite)
- Exposes internal file paths and route structure
- May aid attackers in crafting targeted exploits
- Stack traces reveal ORM layer details

### Note
The /api/Feedbacks and /api/Complaints (plural) endpoints ARE valid routes but require additional parameters (captchaId for Feedbacks, Authorization header for Complaints). The singular forms (/api/Feedback, /api/Complaint) do not exist.