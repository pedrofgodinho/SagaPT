## SQL Injection in POST /remove_request username parameter

**Endpoint:** `POST /remove_request`
**Parameter:** `username` (form field)
**Vulnerability Class:** SQL Injection (Error-based with visible MySQL error)

### Detection Payload
```
POST /remove_request
Content-Type: application/x-www-form-urlencoded
username='&origin=profile
```

### Evidence
- **Normal request** (username=`mr_robot`, origin=`profile`): HTTP 200, response body contains flash message "Friendship request was removed"
- **With SQL payload** (username=`'`, origin=`profile`): HTTP 200, but response body contains visible MySQL error:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'mr_robot') OR (username1 = 'mr_robot' AND username2 = '''')' at line 1")
  ```

The visible MySQL error message directly confirms that the `username` parameter value is being concatenated into a SQL query without proper parameterization. The error reveals the query structure involves `username1` and `username2` fields.

### Additional Notes
- The `origin` parameter on this endpoint was tested with the same payload (`'`) and returned identical results to the baseline — not vulnerable.
- The `/request_friend` endpoint was also tested with the same payload and produced a 500 Internal Server Error, confirming the same underlying vulnerability.
- The application runs on MySQL (Werkzeug/3.0.6 Python/3.8.10 server).
- No Anti-CSRF tokens present on any forms (ZAP alert 10202).