## SQL Injection in /direct_messages?username

**Endpoint:** GET /direct_messages
**Parameter:** username (query parameter)
**Vulnerability Class:** SQL Injection (Error-based)

### Detection

A single quote `'` appended to the `username` query parameter caused the application to return a 500 Internal Server Error, whereas a benign value (e.g., `mr_robot`) returned a normal 200 OK with HTML content.

**Benign request:**
- URL: `http://www.hackergram.com/direct_messages?username=mr_robot`
- Response: 200 OK, HTML page with chat messages

**Injection payload:**
- URL: `http://www.hackergram.com/direct_messages?username=mr_robot'`
- Response: 500 Internal Server Error

**Secondary payload:**
- URL: `http://www.hackergram.com/direct_messages?username=mr_robot'+trash`
- Response: 500 Internal Server Error (identical to above)

### Evidence

The 500 error on the single-quote payload indicates the input is being concatenated into a SQL query without proper parameterization, causing a syntax error when the unescaped quote terminates the string literal prematurely. Both `'` and `' trash` payloads triggered the same 500 error, confirming the error originates from SQL syntax failure, not application logic.

### Risk

High — an attacker can manipulate SQL queries to read, modify, or delete data, or potentially gain server-level access depending on database privileges.

### Recommendation

Use parameterized queries (prepared statements) for all database interactions involving user-supplied input. Never concatenate user input directly into SQL strings.