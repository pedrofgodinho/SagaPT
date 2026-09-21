## JWT Token from SQLi Contains User Password Hash

- **Endpoint:** POST http://juiceshop.local:3000/rest/user/login
- **Parameter:** email (SQL injection)
- **Vulnerability Class:** Information Disclosure / Weak Cryptography
- **Detection Payload:** `' OR '1'='1' -- ` in email field via POST
- **Evidence:** The authentication bypass returned a JWT token containing the full user object in its payload, including:
  - `"password": "0192023a7bbd73250516f069df18b500"` — MD5 hash of admin password
  - `"role": "admin"` — confirms admin privilege
  - `"email": "admin@juice-sh.op"`
  - `"id": 1`
  - `"profileImage": "assets/public/images/uploads/defaultAdmin.png"`
- **Impact:** The JWT payload exposes the admin user's password hash (MD5, which is cryptographically weak and crackable). Combined with the admin role, this enables offline brute-force attacks against the password.
- **Priority:** HIGH - password hash exposure for admin account.