## SQL Injection in POST /request_friend username parameter

**Endpoint:** `POST /request_friend`
**Parameter:** `username` (form field)
**Vulnerability Class:** SQL Injection (Error-based via 500 Internal Server Error)

### Detection Payload
```
POST /request_friend
Content-Type: application/x-www-form-urlencoded
username='
```

### Evidence
- **Normal request** (username=`nonexistent_user_12345`): HTTP 200, response body contains flash message "@nonexistent_user_12345 does not exist"
- **With SQL payload** (username=`'`): HTTP 500 Internal Server Error, generic error page
- **With SQL payload** (username=`' trash`): HTTP 500 Internal Server Error, identical to single quote response

The structural change from 200 to 500 on SQL injection payloads confirms that the `username` parameter value is being concatenated directly into a SQL query without proper parameterization.

### Additional Notes
- The `/remove_request` endpoint was also tested with the same payload and produced a visible MySQL error message (1064), providing even stronger evidence of the same underlying vulnerability.
- The application runs on MySQL (Werkzeug/3.0.6 Python/3.8.10 server).
- No Anti-CSRF tokens present on any forms (ZAP alert 10202).