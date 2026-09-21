## SQL Injection in create_post endpoint (content parameter)

- **Endpoint**: `POST http://www.hackergram.com/create_post`
- **Parameter**: `content` (textarea field, submitted as `application/x-www-form-urlencoded`)
- **Vulnerability class**: SQL Injection (MySQL)
- **Detection payload**: `'` (bare single quote)
- **Evidence**: The response contains a visible MySQL error message:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''''') at line 1")
  ```
- **Response comparison**:
  - Baseline (benign content "This is a test post"): Status 200, "New post published" flash message, page body ~20,043 bytes
  - Payload `'`: Status 200, no flash message, MySQL error displayed in body, page body ~3,720 bytes
  - The dramatic difference in response body and the presence of a raw SQL error confirm the `content` parameter is concatenated into a SQL query without parameterization.
- **Database**: MySQL (error code 1064, error message format matches MySQL/PyMySQL)
- **Risk**: High — direct SQL error disclosure enables further exploitation (data extraction, authentication bypass, etc.)