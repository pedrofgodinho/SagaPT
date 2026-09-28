# Registered Test User Credentials

## User Account
- **Username:** recon_test_user
- **Password:** TestPass123!
- **Email:** recon@test.com
- **User ID (API):** 25
- **User ID (ZAP context):** 168
- **Role:** customer
- **Status:** Active

## Login Endpoint
- **URL:** POST http://juiceshop.local:3000/api/Users/login
- **Fields:** `email` (username field), `password`

## Registration Endpoint
- **URL:** POST http://juiceshop.local:3000/api/Users
- **Fields:** `username`, `password`, `email`, `securityQuestion` (object with `id` and `answer`), `address` (array of objects with `street`, `city`, `state`, `zipCode`, `phone`)
- **Response:** 201 Created with user data and `Location` header

## Security Questions Available (14 total)
1. Your eldest siblings middle name?
2. Mother's maiden name?
3. Mother's birth date? (MM/DD/YY)
4. Father's birth date? (MM/DD/YY)
5. Maternal grandmother's first name?
6. Paternal grandmother's first name?
7. Name of your favorite pet?
8. Last name of dentist when you were a teenager?
9. Your ZIP/postal code when you were a teenager?
10. Company you first work for as an adult?
11. Your favorite book?
12. Your favorite movie?
13. Number of one of your customer or ID cards?
14. What's your favorite place to go hiking?

## Notes for DAST Agent
- User is authenticated via JWT token in `Authorization` header
- User has `customer` role (not admin)
- Registration is publicly accessible (no CAPTCHA or email verification)
- Security questions are publicly listed via API