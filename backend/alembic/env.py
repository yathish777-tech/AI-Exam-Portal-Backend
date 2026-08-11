"""
alembic/env.py
==============
Alembic async migration environment.

DATABASE_URL is read from the environment variable at migration time.
Never hard-code database credentials here.

For async engine (asyncpg driver), we use `run_sync` to execute
migrations in a sync context within the async event loop.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Import Base and all models so Alembic sees the full metadata.
# The models __init__.py re-exports everything.
# ---------------------------------------------------------------------------
from app.core.config import get_settings
from app.models import Base  # noqa: F401  — triggers all model imports

# Alembic config object
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Read DATABASE_URL from the shared application settings.
# ---------------------------------------------------------------------------
def get_database_url() -> str:
    """
    Read DATABASE_URL through app.core.config so Alembic and the app use
    the same .env/environment loading path.

    Raises EnvironmentError if not set, so migrations fail loudly
    rather than silently using a wrong/empty connection.
    """
    url = get_settings().database_url_str
    # Ensure asyncpg driver for async engine
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


# ---------------------------------------------------------------------------
# Offline migrations (generate SQL script without connecting)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (connect to DB and apply)
# ---------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using an async engine."""
    url = get_database_url()
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # No pool for migration runs
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migration."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
