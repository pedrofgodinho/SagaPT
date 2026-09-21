## SQL Injection in edit_post POST endpoint (content parameter)

- **Endpoint**: `POST http://www.hackergram.com/edit_post`
- **Parameter**: `content` (textarea field, submitted as `application/x-www-form-urlencoded`)
- **Vulnerability class**: SQL Injection (MySQL)
- **Detection payload**: `'` (bare single quote appended to content value)
- **Evidence**: The response contains a visible MySQL error message:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '19'' at line 1")
  ```
  The error shows the single quote in the content value was directly concatenated into the SQL query, breaking the syntax.
- **Response comparison**:
  - Baseline (benign content "This is a test post"): Status 200, edit form rendered normally
  - Payload ("This is a test post'"): Status 200, visible MySQL error displayed in page body
- **Database**: MySQL (error code 1064, error message format matches MySQL/PyMySQL)
- **Risk**: High — direct SQL error disclosure enables further exploitation (data extraction, authentication bypass, etc.)