"""
app/repositories/session_repository.py
=======================================
Database operations for the `sessions` table.

SECURITY NOTES:
- current_refresh_token_hash is a SHA-256 digest of the raw token — never raw.
- Queries for active sessions filter on `revoked_at IS NULL`.
- Revocation sets `revoked_at` rather than deleting rows, preserving
  audit history.
- Session lookup checks all rows so revoked rows can reveal token reuse.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import UserSession


class SessionRepository:
    """Data-access layer for UserSession records."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_session(
        self,
        *,
        user_id: uuid.UUID,
        jwt_jti: str,
        current_refresh_token_hash: str,
        ip_address: str | None,
        user_agent: str | None,
        expires_at: datetime,
        token_family_id: uuid.UUID | None = None,
    ) -> UserSession:
        """Insert a new session record and return it."""
        session = UserSession(
            user_id=user_id,
            token_family_id=token_family_id or uuid.uuid4(),
            jwt_jti=jwt_jti,
            current_refresh_token_hash=current_refresh_token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )
        self._db.add(session)
        await self._db.flush()
        await self._db.refresh(session)
        return session

    async def get_by_jti(self, jti: str) -> UserSession | None:
        """
        Return the active session associated with a JWT JTI.

        Only returns sessions where revoked_at IS NULL.
        """
        result = await self._db.execute(
            select(UserSession).where(
                UserSession.jwt_jti == jti,
                UserSession.revoked_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_refresh_token_hash(
        self, token_hash: str
    ) -> UserSession | None:
        """
        Return the session associated with a refresh token hash.

        Returns ALL sessions (including revoked) to support reuse detection.
        Callers must check `session.is_revoked`.
        """
        result = await self._db.execute(
            select(UserSession).where(
                UserSession.current_refresh_token_hash == token_hash,
            )
        )
        return result.scalar_one_or_none()

    async def revoke_session(
        self,
        session_id: uuid.UUID,
        *,
        replaced_by: uuid.UUID | None = None,
    ) -> None:
        """Mark a single session as revoked."""
        values: dict[str, object] = {"revoked_at": datetime.now(timezone.utc)}
        if replaced_by is not None:
            values["replaced_by"] = replaced_by

        await self._db.execute(
            update(UserSession)
            .where(
                UserSession.id == session_id,
                UserSession.revoked_at.is_(None),
            )
            .values(**values)
        )
        await self._db.flush()

    async def revoke_all_user_sessions(self, user_id: uuid.UUID) -> None:
        """Revoke all active sessions for a user (logout-all)."""
        await self._db.execute(
            update(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self._db.flush()

    async def revoke_token_family(self, token_family_id: uuid.UUID) -> None:
        """Revoke every session row in a refresh-token family."""
        await self._db.execute(
            update(UserSession)
            .where(
                UserSession.token_family_id == token_family_id,
                UserSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self._db.flush()

    async def rotate_refresh_token(
        self,
        session_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        token_family_id: uuid.UUID,
        new_jti: str,
        new_refresh_token_hash: str,
        new_expires_at: datetime,
        ip_address: str | None,
        user_agent: str | None,
    ) -> UserSession:
        """
        Create the next refresh-token session and revoke the old token row.

        Keeping the old row with revoked_at set lets the service detect
        replay/reuse of any previously rotated refresh token.
        """
        new_session = await self.create_session(
            user_id=user_id,
            token_family_id=token_family_id,
            jwt_jti=new_jti,
            current_refresh_token_hash=new_refresh_token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=new_expires_at,
        )
        await self.revoke_session(session_id, replaced_by=new_session.id)
        return new_session

    async def update_refresh_token(
        self,
        session_id: uuid.UUID,
        *,
        new_jti: str,
        new_refresh_token_hash: str,
        new_expires_at: datetime,
    ) -> None:
        """
        Rotate the refresh token on an existing session.

        Called during the refresh-token rotation flow:
        - Old refresh token hash is replaced with the new hash.
        - JTI is updated to match the new access token.
        - Expiry is extended.
        """
        await self._db.execute(
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(
                jwt_jti=new_jti,
                current_refresh_token_hash=new_refresh_token_hash,
                expires_at=new_expires_at,
            )
        )
        await self._db.flush()

    async def get_active_sessions(self, user_id: uuid.UUID) -> list[UserSession]:
        """Return all non-revoked, non-expired sessions for a user."""
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            )
        )
        return list(result.scalars().all())
