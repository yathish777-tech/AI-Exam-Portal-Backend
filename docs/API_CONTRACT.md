# LocalSM FE/BE API Contract

Base URL:

- Backend local origin: `http://127.0.0.1:8000`
- API prefix: `/api/v1`
- Frontend env: `VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1`

Authentication:

- Access token is returned in JSON as `data.access_token`.
- Frontend sends protected requests with `Authorization: Bearer <access_token>`.
- Refresh token is set by the backend as an HttpOnly cookie scoped to `/api/v1/auth`.
- Axios must use `withCredentials: true` for refresh-cookie requests.

## Signup

Method: `POST`

Endpoint: `/api/v1/auth/signup`

Authentication: Not required

Request:

```json
{
  "email": "candidate@example.edu",
  "password": "longpassword",
  "role": "CANDIDATE"
}
```

Response `201`:

```json
{
  "success": true,
  "message": "Account created successfully.",
  "data": null,
  "user": {
    "id": "uuid",
    "email": "candidate@example.edu",
    "role": "CANDIDATE",
    "is_active": true,
    "last_login_at": null
  }
}
```

Status codes: `201`, `409`, `422`, `429`, `500`

Notes:

- Backend allows only `CANDIDATE` self-signup.
- Admin and interviewer self-registration are not supported by this endpoint.
- Signup does not return an access token; the frontend logs in after successful student signup.

## Login

Method: `POST`

Endpoint: `/api/v1/auth/login`

Authentication: Not required

Request:

```json
{
  "email": "candidate@example.edu",
  "password": "longpassword"
}
```

Response `200`:

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "access_token": "jwt",
    "token_type": "bearer",
    "expires_in": 900
  },
  "user": {
    "id": "uuid",
    "email": "candidate@example.edu",
    "role": "CANDIDATE",
    "is_active": true,
    "last_login_at": "2026-08-11T00:00:00"
  }
}
```

Status codes: `200`, `401`, `422`, `429`, `500`

## Refresh

Method: `POST`

Endpoint: `/api/v1/auth/refresh`

Authentication: Refresh token cookie preferred, or JSON body refresh token for non-browser clients

Request:

```json
{}
```

Alternative request:

```json
{
  "refresh_token": "refresh-token"
}
```

Response `200`:

```json
{
  "success": true,
  "message": "Tokens refreshed successfully.",
  "data": {
    "access_token": "jwt",
    "token_type": "bearer",
    "expires_in": 900
  },
  "user": null
}
```

Status codes: `200`, `401`, `403`, `422`, `429`, `500`

## Logout

Method: `POST`

Endpoint: `/api/v1/auth/logout`

Authentication: Required

Headers:

```http
Authorization: Bearer <access_token>
```

Request: no body

Response `200`:

```json
{
  "success": true,
  "message": "Logged out successfully.",
  "error_code": null
}
```

Status codes: `200`, `401`, `429`, `500`

## Logout All

Method: `POST`

Endpoint: `/api/v1/auth/logout-all`

Authentication: Required

Headers:

```http
Authorization: Bearer <access_token>
```

Request: no body

Response `200`:

```json
{
  "success": true,
  "message": "All sessions have been terminated.",
  "error_code": null
}
```

Status codes: `200`, `401`, `429`, `500`

## Current User

Method: `GET`

Endpoint: `/api/v1/auth/me`

Authentication: Required

Headers:

```http
Authorization: Bearer <access_token>
```

Response `200`:

```json
{
  "id": "uuid",
  "email": "candidate@example.edu",
  "role": "CANDIDATE",
  "is_active": true,
  "last_login_at": "2026-08-11T00:00:00"
}
```

Status codes: `200`, `401`, `429`, `500`

## Forgot Password

Method: `POST`

Endpoint: `/api/v1/auth/forgot-password`

Authentication: Not required

Request:

```json
{
  "email": "candidate@example.edu"
}
```

Response `200`:

```json
{
  "success": true,
  "message": "If an account with that email exists, a password reset code has been sent. Please check your email.",
  "error_code": null
}
```

Status codes: `200`, `422`, `429`, `500`

## Verify OTP

Method: `POST`

Endpoint: `/api/v1/auth/verify-otp`

Authentication: Not required

Request:

```json
{
  "email": "candidate@example.edu",
  "otp": "123456"
}
```

Response `200`:

```json
{
  "success": true,
  "message": "OTP verified. You may now reset your password.",
  "error_code": null
}
```

Status codes: `200`, `401`, `422`, `429`, `500`

## Reset Password

Method: `POST`

Endpoint: `/api/v1/auth/reset-password`

Authentication: Not required

Request:

```json
{
  "email": "candidate@example.edu",
  "otp": "123456",
  "new_password": "newlongpassword"
}
```

Response `200`:

```json
{
  "success": true,
  "message": "Password has been reset successfully. All existing sessions have been terminated. Please log in again.",
  "error_code": null
}
```

Status codes: `200`, `401`, `422`, `429`, `500`
