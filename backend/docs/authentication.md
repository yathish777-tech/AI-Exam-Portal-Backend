# Authentication

The backend uses short-lived JWT access tokens and rotating refresh tokens.

## Token Flow

1. `POST /api/v1/auth/login` verifies email and password.
2. The server creates a session row with a JWT `jti` and hashed refresh token.
3. The response body returns only the access token.
4. The raw refresh token is set as an HttpOnly cookie for browser clients.
5. `POST /api/v1/auth/refresh` validates and rotates the refresh token.
6. `POST /api/v1/auth/logout` revokes the current session.
7. `POST /api/v1/auth/logout-all` revokes all sessions for the current user.

Non-browser clients may send `refresh_token` in the refresh request body. The
refresh token must not be used as a bearer token for protected API routes.

## JWT Claims

Access tokens contain the minimum server-required claims:

```json
{
  "sub": "user_uuid",
  "jti": "token_uuid",
  "type": "access",
  "role": "CANDIDATE",
  "iat": 0,
  "exp": 0
}
```

The `role` claim is informational. Authorization uses the database-loaded user
role through `get_current_user()` and `require_role()`.

## Refresh Token Storage

Raw refresh tokens are never stored. The `sessions.current_refresh_token_hash`
column stores a SHA-256 hash of the high-entropy raw refresh token. Rotation
creates a new session row in the same `token_family_id`, revokes the previous
row, and records the replacement in `replaced_by`.

Submitting an already-revoked refresh token is treated as replay detection and
revokes the token family.

## Required Environment

```env
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=<strong-random-secret>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

For asymmetric JWT algorithms, configure:

```env
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY=<pem-private-key>
JWT_PUBLIC_KEY=<pem-public-key>
```

Production startup fails if required key material is missing or insecure.
