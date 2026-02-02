"""
Verification Token Repository - Database access layer for verification tokens
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.auth.src.models.verification_token import VerificationTokenORM
from services.auth.src.domain.user import VerificationToken


class VerificationTokenRepository:
    """Repository for VerificationToken aggregate"""

    def __init__(self, db: Session):
        self.db = db

    def save(self, token: VerificationToken) -> VerificationTokenORM:
        """Save verification token to database"""
        orm = VerificationTokenORM(
            token=token.token,
            user_id=token.user_id,
            expires_at=token.expires_at,
            used=token.used,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm

    def get_by_token(self, token: str) -> Optional[VerificationTokenORM]:
        """Get verification token by token string"""
        query = select(VerificationTokenORM).where(VerificationTokenORM.token == token)
        return self.db.scalars(query).first()

    def get_by_user_id(self, user_id: UUID) -> Optional[VerificationTokenORM]:
        """Get latest verification token for user"""
        query = (
            select(VerificationTokenORM)
            .where(VerificationTokenORM.user_id == user_id)
            .order_by(VerificationTokenORM.created_at.desc())
        )
        return self.db.scalars(query).first()

    def mark_as_used(self, token_str: str) -> bool:
        """Mark token as used"""
        token = self.get_by_token(token_str)
        if not token:
            return False

        token.used = True
        self.db.commit()
        return True

    def clean_expired(self) -> int:
        """Delete expired tokens. Returns number deleted."""
        now = datetime.now(timezone.utc)
        query = select(VerificationTokenORM).where(
            VerificationTokenORM.expires_at < now
        )
        tokens = self.db.scalars(query).all()
        count = len(tokens)

        for token in tokens:
            self.db.delete(token)

        self.db.commit()
        return count
