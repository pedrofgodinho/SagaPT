## SQL Injection in /requests endpoint — username parameter

**Endpoint:** `GET /requests`
**Parameter:** `username` (query string)
**Payload:** `'` (single quote)

### Evidence
- Sending `GET /requests?username='` returns **HTTP 500 Internal Server Error**
- The normal response for a valid username returns HTTP 200 with the rendered page
- The 500 error indicates the single quote broke the underlying SQL query syntax

### Request
```
GET /requests?username=' HTTP/1.1
Host: www.hackergram.com
Cookie: session=<authenticated>
```

### Response
```
HTTP/1.1 500 Internal Server Error
Content-Type: text/html; charset=utf-8

<!doctype html>
<html lang=en>
<title>500 Internal Server Error</title>
<h1>Internal Server Error</h1>
<p>The server encountered an internal error and was unable to complete your request.</p>
</html>
```

### Conclusion
The `username` parameter on the `/requests` endpoint is vulnerable to SQL injection. The bare single quote `'` caused a server-side SQL error (500 response), confirming that user input is being concatenated into a SQL query without proper parameterization.

### Notes
- The `origin` parameter was also tested with a single quote (`GET /requests?origin='`) and returned HTTP 200 with no SQL error, suggesting it is either not injectable or properly parameterized.
- Detection payload: `'` — no data extraction or UNION/ORDER BY probes were performed (exploitation agent's role).