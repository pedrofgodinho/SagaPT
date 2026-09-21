# Authentication Setup - JWT Limitation

## Problem
The target application (OWASP Juice Shop) uses **JWT Bearer token authentication**, but the `register_credentials` tool only supports **form-based (cookie) authentication**.

## Evidence
- **Login endpoint:** `POST /rest/user/login`
- **Request body:** `{"email": "recon@test.com", "password": "ReconPass123!"}`
- **Response:** HTTP 200 with JWT token in `authentication.token` field
- **Response body:** `{"authentication":{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...","bid":6,"umail":"recon@test.com"}}`
- **No Set-Cookie header** in the login response — the app does not use session cookies

## Auth Verification Results
All authenticated endpoint tests returned **401 Unauthorized**:
- `GET /api/Users/1` → 401: "No Authorization header was found"
- `GET /api/Users` → 401: "No Authorization header was found"
- `GET /api/SecurityQuestions/1` → 401: "No Authorization header was found"

## Root Cause
The `register_credentials` ZAP tool configures a form-based authentication context that:
1. Performs a login POST and expects cookies in the response
2. Automatically attaches those cookies to subsequent requests

But Juice Shop's `/rest/user/login`:
1. Returns a JWT token in the JSON response body (no cookies)
2. Requires the token to be sent as `Authorization: Bearer <token>` header

These mechanisms are incompatible — the ZAP proxy has no way to extract the JWT from the response body and inject it into subsequent requests.

## Required Fix (External)
To enable authenticated scanning, the ZAP context would need to be configured with a custom authentication script that:
1. Performs the POST to `/rest/user/login`
2. Extracts the `authentication.token` value from the JSON response
3. Adds `Authorization: Bearer <token>` to every subsequent request

This capability is **outside the scope of the available tools**. The DAST agent will need to either:
- Use a custom ZAP authentication script, or
- Manually inject the JWT token via the `Authorization` header for each authenticated request