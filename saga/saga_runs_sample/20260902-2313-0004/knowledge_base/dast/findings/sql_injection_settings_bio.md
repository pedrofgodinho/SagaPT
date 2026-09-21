## SQL Injection in /settings POST — bio parameter

- **Endpoint:** `POST /settings`
- **Parameter:** `bio`
- **Payload:** `' trash`
- **Detection:** The application returned a visible MySQL syntax error in the HTML response:
  ```
  (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'trash', photo='mrrobot.png' WHERE username = 'mr_robot'' at line 1")
  ```
- **Evidence:** The error reveals the injected `' trash` payload was concatenated directly into a SQL UPDATE statement without parameterization. The error was returned with HTTP 200 status.
- **Notes:** The `currentpassword` was set to the correct value (`elliot123`) to allow the update query to execute. The error confirms the `bio` parameter is directly interpolated into SQL.