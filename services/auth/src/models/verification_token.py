"""
Email Verification Token ORM Model
Tracks one-time tokens sent to users for email verification
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID as UUID_TYPE
from sqlalchemy.orm import Mapped, mapped_column

from services.auth.src.models import Base


class VerificationTokenORM(Base):
    """Email verification token database model"""
    __tablename__ = "verification_tokens"

    token: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        nullable=False,
        unique=True
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID_TYPE(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_verification_tokens_user_id", "user_id"),
        Index("idx_verification_tokens_expires_at", "expires_at"),
        Index("idx_verification_tokens_used", "used"),
    )

    def __repr__(self) -> str:
        return f"<VerificationTokenORM(user_id={self.user_id}, used={self.used})>"
