## Application Error Disclosure (Stack Trace)

**Endpoint:** POST /rest/user/login
**Trigger:** Any input that causes a server-side error (e.g., SQL injection payload `' trash`)
**Vulnerability Class:** Sensitive Information Exposure

### Detection

When a malformed input is sent to the login endpoint (e.g., `' trash` in the email field), the application returns an HTTP 500 error with a full server-side stack trace in the HTML response body.

### Evidence

Request: `POST /rest/user/login` with body `{"email": "' trash", "password": "anything"}`
Response: HTTP 500 with body containing:
```html
<h1>OWASP Juice Shop (Express ^4.22.1)</h1>
<h2><em>500</em> Error</h2>
<ul id="stacktrace">
  <li>  at Database.<anonymous> (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:185:27)</li>
  <li>  at /juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:183:50</li>
  <li>  at new Promise (<anonymous>)</li>
  <li>  at Query.run (/juice-shop/node_modules/sequelize/lib/dialects/sqlite/query.js:183:12)</li>
  <li>  at /juice-shop/node_modules/sequelize/lib/sequelize.js:315:28</li>
  <li>  at process.processTicksAndRejections (node:internal/process/task_queues:104:2)</li>
</ul>
```

### Impact

Stack traces reveal:
- Application framework: Express.js ^4.22.1
- ORM: Sequelize
- Database: SQLite
- Exact file paths and line numbers in the application codebase
- Node.js module paths, aiding in targeted exploits against specific versions

### Recommendation

Configure Express to suppress stack traces in production responses. Use a custom error handler middleware that returns generic error messages to clients while logging full details server-side.