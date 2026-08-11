# FE/BE Integration Report

Date: 2026-08-11

Project: LocalSM Secure AI Exam Portal

## Summary

Frontend APIs found: 16 service methods in `frontend/src/services/api.js`

Backend APIs found: 9 registered API v1 endpoints, all under `/api/v1/auth`

Matching APIs after fixes: 5 frontend service methods

Mismatched or pending APIs: 11 frontend service methods plus 4 backend auth endpoints with no frontend UI flow

Fixed in this pass: 5

Pending: student exam APIs, interviewer APIs, admin APIs, proctoring log API, forgot/reset password UI wiring, logout-all UI wiring, automatic refresh retry

## Registered Backend Routes

| API | Method | Backend Endpoint | Auth | Role |
|-----|--------|------------------|------|------|
| Signup | POST | `/api/v1/auth/signup` | No | Self-signup restricted to `CANDIDATE` |
| Login | POST | `/api/v1/auth/login` | No | Any active account |
| Refresh | POST | `/api/v1/auth/refresh` | Refresh cookie/body | Any active session |
| Logout | POST | `/api/v1/auth/logout` | Bearer token | Any authenticated user |
| Logout All | POST | `/api/v1/auth/logout-all` | Bearer token | Any authenticated user |
| Current User | GET | `/api/v1/auth/me` | Bearer token | Any authenticated user |
| Forgot Password | POST | `/api/v1/auth/forgot-password` | No | Any |
| Verify OTP | POST | `/api/v1/auth/verify-otp` | No | Any |
| Reset Password | POST | `/api/v1/auth/reset-password` | No | Any |

## Frontend vs Backend Comparison

| Feature | Frontend Before | Backend | Status |
|---------|-----------------|---------|--------|
| API base URL | Defaulted to `/api/v1`; no local backend origin in env example | `/api/v1` mounted on FastAPI origin | FIXED |
| Login | Mock `authService.login`; UI bypassed service and generated demo user | `POST /api/v1/auth/login` with `{ email, password }` | FIXED |
| Signup | Mock `authService.register`; UI sent `{ name, email, domain }` to local state | `POST /api/v1/auth/signup` with `{ email, password, role: CANDIDATE }` | FIXED for student |
| Current User | Mock localStorage read | `GET /api/v1/auth/me` with bearer token | FIXED in service |
| Logout | Frontend local state clear only | `POST /api/v1/auth/logout` with bearer token | FIXED |
| Refresh | No frontend flow | `POST /api/v1/auth/refresh` with HttpOnly cookie/body | MATCH in service, pending automatic retry flow |
| Logout All | No frontend call | `POST /api/v1/auth/logout-all` | PENDING |
| Forgot Password | No frontend call | `POST /api/v1/auth/forgot-password` | PENDING |
| Verify OTP | No frontend call | `POST /api/v1/auth/verify-otp` | PENDING |
| Reset Password | No frontend call | `POST /api/v1/auth/reset-password` | PENDING |
| Upcoming Interviews | Placeholder `GET /student/interviews/upcoming` | No registered backend route | PENDING |
| Completed Interviews | Placeholder `GET /student/interviews/completed` | No registered backend route | PENDING |
| Exam Questions | Placeholder `GET /student/exam/:interviewId/questions` | No registered backend route | PENDING |
| Submit Exam Answers | Placeholder `POST /student/exam/:interviewId/submit` | No registered backend route | PENDING |
| Upload Question PDF | Placeholder `POST /interviewer/upload-pdf` multipart | No registered backend route | PENDING |
| Candidates | Placeholder `GET /interviewer/candidates` | No registered backend route | PENDING |
| Leaderboard | Placeholder `GET /interviewer/leaderboard` | No registered backend route | PENDING |
| Admin Analytics | Placeholder `GET /admin/analytics` | No registered backend route | PENDING |
| Admin Students | Placeholder `GET /admin/students` | No registered backend route | PENDING |
| Admin Interviewers | Placeholder `GET /admin/interviewers` | No registered backend route | PENDING |
| Proctoring Log | Placeholder `POST /proctoring/:interviewId/log` | No registered backend route | PENDING |

## Request/Response Mismatches Found

| Area | Frontend | Backend | Resolution |
|------|----------|---------|------------|
| Login endpoint | Planned `/auth/{role}/login` | `/auth/login` | Frontend now calls `/auth/login` |
| Login identifier | Admin UI allowed username `admin` | Backend requires email | Frontend still displays username/email, but backend validation requires a valid email |
| Signup endpoint | Planned `/auth/{role}/register` | `/auth/signup` | Frontend now calls `/auth/signup` |
| Signup fields | `{ name, email, domain }` plus local password | Backend forbids extras and expects `{ email, password, role }` | Frontend now sends backend-safe body |
| Signup role | `student` / `interviewer` | Only `CANDIDATE` self-signup | Student maps to `CANDIDATE`; interviewer self-registration shows backend-compatible error |
| Signup token | Frontend assumed registered user could enter dashboard | Backend signup response has no access token | Frontend logs in after successful student signup |
| Token field | Frontend previously fabricated `token_mock_*` | Backend returns `data.access_token` | Frontend stores `data.access_token` |
| User role | Frontend uses `student` | Backend returns `CANDIDATE` | Frontend maps `CANDIDATE` to `student` |
| Refresh token | Frontend had no cookie support | Backend uses HttpOnly refresh cookie | Axios now uses `withCredentials: true`; automatic retry remains pending |

## Authentication Status

Authentication integration: Partially integrated and code-wired for login, student signup, current user service, and logout.

JWT status: Access token is stored under `exam_portal_token` and sent as `Authorization: Bearer <token>`.

Refresh-token status: Backend secure cookie design is preserved. Frontend service can call refresh with credentials, but automatic token refresh/retry is not implemented yet.

Logout status: Frontend now calls backend logout and then clears local auth state.

RBAC status: Backend roles are `ADMIN`, `INTERVIEWER`, `CANDIDATE`; frontend roles are `admin`, `interviewer`, `student`. Mapping is implemented for auth responses. Full RBAC cannot be verified until non-auth protected routes are registered.

## CORS Status

Backend CORS is configured securely in `backend/app/main.py`:

- `allow_origins=[settings.frontend_url]`
- `allow_credentials=True`
- no wildcard origin
- explicit allowed headers

Required local backend env:

```env
FRONTEND_URL=http://localhost:3000
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

Required local frontend env:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

If the browser origin is `http://127.0.0.1:3000` instead of `http://localhost:3000`, `FRONTEND_URL` must exactly match that origin.

## Files Changed

Frontend:

- `frontend/src/services/api.js`
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/components/forms/LoginForm.jsx`
- `frontend/src/components/forms/RegisterForm.jsx`
- `frontend/src/utils/storage.js`
- `frontend/.env.example`

Backend:

- No backend source code changed.

Docs:

- `docs/API_CONTRACT.md`
- `docs/FE_BE_INTEGRATION_REPORT.md`

## Test Status

Static inspection: Completed.

Frontend type-check: Passed with `npm.cmd run lint`.

Frontend build: Blocked by Windows/esbuild path resolution before app compilation. The project path contains `INTERNSHIP'`, and esbuild reports it cannot resolve `vite.config.ts` and cannot read a parent directory. Retrying through a temporary junction produced the same failure because `node_modules` still resolves to the original path.

Backend compile: Passed with `python -m compileall app`.

Backend dependency check: Passed with `pip check`.

Backend tests: Passed with `python -m pytest tests -v` (`7 passed`, `1 warning`).

Signup browser test: Not run; requires PostgreSQL, backend env, backend server, and frontend server.

Login browser test: Not run; requires seeded users and running services.

Protected API test: Not run end-to-end; service code is wired for bearer token.

Logout browser test: Not run end-to-end; service code is wired.

Refresh-token test: Not run end-to-end; service method exists, automatic retry pending.

## Remaining Integration Issues

1. Backend only registers auth routes. Student, interviewer, admin, exam, question, submission, result, and proctoring API modules are empty or not included.
2. Frontend pages still rely on mock data for dashboards, interviews, MCQ tests, admin lists, and interviewer workflows.
3. Interviewer self-registration exists in the UI, but backend security policy permits only candidate self-signup.
4. Admin login UI allows username, but backend accepts email only.
5. Forgot password, OTP verification, reset password, logout-all, and automatic refresh-token retry are not exposed in frontend UI flows.
6. Full RBAC cannot be verified until protected role-specific backend routes are implemented and registered.
