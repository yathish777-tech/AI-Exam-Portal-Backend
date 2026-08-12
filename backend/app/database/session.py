"""
app/database/session.py
=======================
Async SQLAlchemy engine and session factory.

SECURITY / CONFIGURATION NOTES:
- DATABASE_URL must be set via environment variable — never hard-code.
- Use a least-privilege PostgreSQL role for the application user.
- Pool settings (pool_size, max_overflow, pool_timeout) must be tuned
  for your production load; the defaults here are conservative.
- echo=True logs SQL statements — ONLY enable in DEBUG mode because
  log output may contain query parameter values.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# `pool_pre_ping=True` issues a cheap "SELECT 1" before handing a
# connection from the pool, recovering from stale connections after
# network interruptions.
#
# `echo` is intentionally tied to DEBUG mode only. In production DEBUG
# must be False so SQL is never written to logs.
# ---------------------------------------------------------------------------
engine: AsyncEngine = create_async_engine(
    settings.database_url_str,  # SecretStr.get_secret_value() via property
    echo=settings.debug,
    pool_pre_ping=True,
    # Pool settings are read from environment variables so they can be tuned
    # per deployment without changing code. Defaults are conservative and safe.
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# `expire_on_commit=False` prevents attribute access errors after commit
# when running in async context — the session is closed after the request.
# ---------------------------------------------------------------------------
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
