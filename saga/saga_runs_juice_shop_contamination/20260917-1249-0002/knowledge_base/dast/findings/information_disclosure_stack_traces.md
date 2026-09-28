## Information Disclosure - Stack Traces in Error Responses

- **Endpoint:** Multiple endpoints trigger stack traces (GET /rest/user/login, GET /rest/products, GET /rest/users/me, GET /ftp/..%2f..%2f..%2fetc%2fpasswd, etc.)
- **Evidence:** When invalid paths or methods are used, the application returns 500 errors with full Express/Node.js stack traces including:
  - Full file paths: `/juice-shop/build/routes/angular.js:18:18`
  - Framework version: `OWASP Juice Shop (Express ^4.22.1)`
  - Internal middleware paths: `/juice-shop/build/lib/utils.js:235:26`, `/juice-shop/build/lib/insecurity.js:218:5`
  - Example error: "Error: Unexpected path: /rest/user/login" with full stack trace
- **Impact:** Attackers can enumerate internal file structure, application architecture, and technology stack, aiding further attacks.
- **Risk:** Medium
