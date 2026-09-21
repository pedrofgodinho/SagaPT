## Application Error Disclosure (Stack Trace Exposure)

- **Endpoint:** POST http://juiceshop.local:3000/rest/user/registration (and other invalid paths)
- **Vulnerability Class:** Information Disclosure
- **Evidence:** Invalid/unknown endpoints return HTTP 500 with full Express.js stack traces in the HTML body, including:
  - Application version: "OWASP Juice Shop (Express ^4.22.1)"
  - Full file paths: `/juice-shop/build/routes/angular.js:18:18`, `/juice-shop/build/lib/utils.js:235:26`, `/juice-shop/node_modules/express/lib/router/layer.js:95:5`, etc.
  - Complete call stack showing internal file structure and line numbers
- **Impact:** Stack traces reveal application architecture, framework versions, and internal file paths that aid attackers in crafting targeted exploits.
- **Priority:** LOW