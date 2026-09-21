# Authentication Setup for DAST Agent

## Test Account Created
- **Email:** test@test.com
- **Password:** Test1234!
- **User ID:** 25
- **Role:** customer
- **Status:** active

## Registration Endpoint
- **URL:** `POST /api/users`
- **Content-Type:** `application/json`
- **Body:** `{"email":"test@test.com","password":"Test1234!","name":"Test User","passwordVerification":"Test1234!"}`
- **Response:** 201 Created with user data

## Login Endpoint
- **URL:** `POST /rest/user/login`
- **Content-Type:** `application/json`
- **Body:** `{"email":"test@test.com","password":"Test1234!"}`
- **Response:** 200 OK with JWT token:
  ```json
  {
    "authentication": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.<payload>.<signature>",
      "bid": 6,
      "umail": "test@test.com"
    }
  }
  ```

## How to Authenticate Protected Endpoints
This app uses JWT token authentication. Add the following header to requests:
```
Authorization: Bearer <token>
```

## ZAP Configuration
- Form-based authentication configured in ZAP context (user_id: 380)
- Login URL: `http://juiceshop.local:3000/rest/user/login`
- Username field: `email`
- Password field: `password`
- **Note:** ZAP forced user mode may not auto-attach JWT tokens. DAST agent should manually include `Authorization: Bearer <token>` header for authenticated requests.

## Authenticated Endpoints to Test
- `GET /api/Users/{id}` - IDOR potential
- `GET /api/PrivacyRequests` - Privacy request management
- `POST /api/Feedback` - Feedback submission
- `POST /api/Complaint` - Complaint submission
- `GET/POST /api/Order` - Order management
- `GET/POST /api/Coupons` - Coupon management
- `POST /api/SupportTickets` - Support tickets
- `POST /api/Recycle` - Recycling returns