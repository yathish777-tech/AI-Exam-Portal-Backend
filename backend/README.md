# LocalSM Secure AI Exam Portal — Backend

Production-oriented backend for the LocalSM Secure AI Exam Portal.

## Backend Running cmd:
 - alembic upgrade head
 - uvicorn app.main:app --reload


## 🚀 Tech Stack

- Python 3.14+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- asyncpg
- Pydantic v2
- JWT Authentication
- bcrypt
- Loguru
- SlowAPI
- WebSockets / Socket.IO
- OpenCV
- PyTorch
- Pytest

---

## 📁 Project Structure

```text
backend/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── router.py
│   │       └── ...
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   ├── permissions.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── dependencies.py
│   │
│   ├── dependencies/
│   │   ├── auth.py
│   │   ├── roles.py
│   │   └── common.py
│   │
│   ├── middleware/
│   │   ├── request_id.py
│   │   ├── security_headers.py
│   │   ├── rate_limit.py
│   │   ├── logging.py
│   │   └── error_handler.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── role_permission.py
│   │   ├── session.py
│   │   └── otp.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── session_repository.py
│   │   ├── role_repository.py
│   │   └── otp_repository.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   └── user.py
│   │
│   ├── services/
│   │   └── auth_service.py
│   │
│   └── main.py
│
├── alembic/
│   ├── versions/
│   │   └── 0001_auth_tables.py
│   └── env.py
│
├── tests/
├── docs/
├── logs/
├── uploads/
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── README.md