"""
app/database/dependencies.py
============================
FastAPI dependency that provides a per-request async database session.

Usage in route handlers:
    from app.database.dependencies import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an AsyncSession scoped to a single HTTP request.

    The session is:
    - Committed if the request handler completes without raising.
    - Rolled back and closed if any exception is raised during the request.

    NOTE: Explicit transaction management (begin/commit/rollback) inside
    service and repository functions should use `db.begin()` context managers
    or the session's autobegin behaviour (SQLAlchemy 2.0 default).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
