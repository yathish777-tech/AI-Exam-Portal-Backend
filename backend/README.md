# LocalSM Secure AI Exam Portal — Backend

Production-oriented REST API backend for the LocalSM AI-powered examination platform.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14+ |
| Web Framework | FastAPI 0.115+ |
| Database | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.x (async) |
| Migrations | Alembic |
| DB Driver | asyncpg |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt + HMAC-OTP |
| Rate Limiting | SlowAPI |
| Logging | Loguru (structured JSON) |
| Testing | pytest + pytest-asyncio + httpx |

---

## Project Structure

```
backend/
│
├── app/
│   ├── api/v1/
│   │   ├── auth.py          ← Authentication endpoints
│   │   ├── health.py        ← Readiness probe endpoint
│   │   └── router.py        ← API v1 top-level router
│   │
│   ├── core/
│   │   ├── config.py        ← pydantic-settings configuration
│   │   ├── constants.py     ← Enums and project-wide constants
│   │   ├── exceptions.py    ← Application exception hierarchy
│   │   ├── logging.py       ← Loguru setup and security event logging
│   │   ├── permissions.py   ← Role-based permission checks
│   │   └── security.py      ← JWT, bcrypt, OTP, refresh token primitives
│   │
│   ├── database/
│   │   ├── base.py          ← DeclarativeBase, UUIDMixin, TimestampMixin
│   │   ├── session.py       ← Async engine and session factory
│   │   └── dependencies.py  ← Per-request AsyncSession DI dependency
│   │
│   ├── dependencies/
│   │   ├── auth.py          ← JWT validation / current user dependency
│   │   ├── roles.py         ← Role-enforcement dependencies
│   │   └── common.py        ← Request ID, client IP, user agent helpers
│   │
│   ├── middleware/
│   │   ├── request_id.py    ← X-Request-ID correlation ID
│   │   ├── security_headers.py ← Security HTTP headers
│   │   ├── logging.py       ← Structured request/response logging
│   │   ├── rate_limit.py    ← SlowAPI rate limiter
│   │   └── error_handler.py ← Global exception handlers
│   │
│   ├── models/
│   │   ├── user.py          ← User ORM model
│   │   ├── role.py          ← Role ORM model
│   │   ├── permission.py    ← Permission ORM model
│   │   ├── role_permission.py ← Role-Permission join table
│   │   ├── session.py       ← UserSession ORM model (refresh tokens)
│   │   └── otp.py           ← PasswordResetOTP ORM model
│   │
│   ├── repositories/
│   │   ├── base.py          ← Generic BaseRepository[T]
│   │   ├── user_repository.py
│   │   ├── session_repository.py
│   │   ├── role_repository.py
│   │   └── otp_repository.py
│   │
│   ├── schemas/             ← Pydantic request/response schemas
│   ├── services/
│   │   └── auth_service.py  ← Authentication business logic
│   │
│   └── main.py              ← Application factory + lifespan
│
├── alembic/
│   ├── env.py               ← Async Alembic environment
│   └── versions/
│       ├── 0001_auth_tables.py
│       └── 0002_session_replaced_by.py
│
├── tests/
│   ├── conftest.py          ← Shared pytest fixtures
│   ├── unit/
│   │   ├── test_foundation.py  ← Phase 1 infrastructure tests
│   │   ├── test_security.py    ← JWT, OTP, bcrypt tests
│   │   └── test_auth.py        ← Auth schema tests
│   └── integration/            ← Tests requiring a real DB
│
├── .env.example             ← Environment variable template (copy to .env)
├── alembic.ini
├── pyproject.toml           ← pytest, ruff, mypy, coverage config
└── requirements.txt
```

---

## Setup Guide

### 1 — Clone and enter the backend directory

```powershell
cd backend
```

### 2 — Create a Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3 — Install dependencies

```powershell
pip install -r requirements.txt
```

### 4 — Configure environment variables

Copy the template and fill in your values:

```powershell
copy .env.example .env
```

Open `.env` and configure at minimum:

```env
ENVIRONMENT=development
DEBUG=true

DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/exam_portal

# Generate with: python -c "import secrets; print(secrets.token_hex(64))"
JWT_SECRET_KEY=<64-char-hex-string>
JWT_ALGORITHM=HS256

# Generate independently from JWT_SECRET_KEY
OTP_HASH_SECRET=<64-char-hex-string>

FRONTEND_URL=http://localhost:5173
COOKIE_SECURE=false
LOG_FORMAT=text
```

> **Security**: Never commit `.env`. It is in `.gitignore`.

### 5 — Set up PostgreSQL

Make sure PostgreSQL is running. Create the database and application user:

```sql
CREATE DATABASE exam_portal;
CREATE USER exam_app WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE exam_portal TO exam_app;
```

The application requires the `citext` extension (created automatically by migration 0001).
Your PostgreSQL user needs `SUPERUSER` or `CREATEROLE` privilege for the first migration.

### 6 — Run Alembic migrations

```powershell
alembic upgrade head
```

Check the current migration state:

```powershell
alembic current
```

> **Important**: Never use `Base.metadata.create_all()` in production. Always use Alembic.

### 7 — Start the development server

```powershell
uvicorn app.main:app --reload
```

The server starts on `http://127.0.0.1:8000`.

---

## API Endpoints

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe (no DB check) |
| `GET` | `/api/v1/health` | Readiness probe (includes DB probe) |

### Authentication

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/signup` | Register a new CANDIDATE account |
| `POST` | `/api/v1/auth/login` | Authenticate and receive tokens |
| `POST` | `/api/v1/auth/refresh` | Rotate refresh token |
| `POST` | `/api/v1/auth/logout` | Revoke current session |
| `POST` | `/api/v1/auth/logout-all` | Revoke all sessions |
| `GET` | `/api/v1/auth/me` | Get current user profile |
| `POST` | `/api/v1/auth/forgot-password` | Initiate OTP password reset |
| `POST` | `/api/v1/auth/verify-otp` | Verify OTP |
| `POST` | `/api/v1/auth/reset-password` | Complete password reset |

---

## Swagger / OpenAPI

Available in `DEBUG=true` mode:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Swagger is **disabled in production** (`DEBUG=false`).

---

## Running Tests

Run all unit tests:

```powershell
pytest tests/unit/ -v
```

Run with coverage:

```powershell
pytest tests/unit/ -v --cov=app --cov-report=term-missing
```

Run a specific test file:

```powershell
pytest tests/unit/test_foundation.py -v
```

Run only security tests:

```powershell
pytest -m security -v
```

> Unit tests do **not** require a running database. They use mocks and `monkeypatch`
> to isolate all infrastructure dependencies.

Integration tests (require a real test DB — set `TEST_DATABASE_URL` in `.env`):

```powershell
pytest tests/integration/ -v -m integration
```

---

## Alembic Cheat Sheet

| Command | Purpose |
|---|---|
| `alembic upgrade head` | Apply all pending migrations |
| `alembic current` | Show current migration revision |
| `alembic history` | Show full migration history |
| `alembic downgrade -1` | Roll back the last migration |
| `alembic revision --autogenerate -m "description"` | Generate a new migration from model changes |

> **Migration safety**: Always review autogenerated migrations before applying.
> Check for unintended DROP TABLE, DROP COLUMN, or data-loss operations.

---

## Generating Secrets

```powershell
# JWT_SECRET_KEY (256-bit minimum)
python -c "import secrets; print(secrets.token_hex(64))"

# OTP_HASH_SECRET (independent from JWT key)
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Security Architecture

| Feature | Implementation |
|---|---|
| Password hashing | bcrypt (configurable rounds, min 12) |
| JWT signing | HS256/RS256 (algorithm fixed server-side, alg=none rejected) |
| Refresh tokens | SHA-256 hash stored, raw token sent as HttpOnly cookie |
| OTP hashing | HMAC-SHA256 with server secret (not plain SHA-256) |
| Token rotation | Refresh token reuse detection via token family |
| CORS | Origin allowlist from env (no wildcards with credentials) |
| Rate limiting | Per-IP via SlowAPI (env-configurable limits) |
| SQL injection | SQLAlchemy parameterized queries (no string interpolation) |
| Request ID | UUID4 per request (client-provided ID validated) |
| Secrets | `SecretStr` throughout (never appear in logs/repr) |
| Session revocation | Server-side JTI lookup (logout invalidates token immediately) |

---

## Environment Variables Reference

See [`.env.example`](.env.example) for the full list with descriptions.

---

## Known Limitations

- Rate limiter uses in-memory storage. For multi-instance deployments,
  configure a shared Redis backend (`RATE_LIMIT_STORAGE_URI`).
- Email delivery (OTP sending) requires integration with an email service —
  the placeholder in `auth.py` must be connected to your email provider.
- AI/proctoring features (OpenCV, PyTorch) are not yet implemented — Phase 2+.