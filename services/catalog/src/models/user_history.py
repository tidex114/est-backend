"""
User History ORM Model
Tracks user actions (reservations, cancellations, etc) for future analytics
Structure only - not implemented yet, but ready for future use
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import String, DateTime, Enum as SQLEnum, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from services.catalog.src.models.base import Base


class UserAction(str, Enum):
    """Types of user actions to track"""
    OFFER_VIEWED = "offer_viewed"
    OFFER_RESERVED = "offer_reserved"
    OFFER_CANCELLED = "offer_cancelled"
    OFFER_COMPLETED = "offer_completed"
    OFFER_EXPIRED = "offer_expired"


class UserHistoryORM(Base):
    """User activity history database model"""
    __tablename__ = "user_history"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User who performed the action"
    )

    offer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Offer related to the action"
    )

    action: Mapped[UserAction] = mapped_column(
        SQLEnum(UserAction, name="user_action"),
        nullable=False,
        index=True,
    )

    details: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="Additional action details (JSON format future)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_user_history_user_id", "user_id"),
        Index("idx_user_history_offer_id", "offer_id"),
        Index("idx_user_history_action", "action"),
        Index("idx_user_history_created_at", "created_at"),
        Index("idx_user_history_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<UserHistoryORM(user_id={self.user_id}, action={self.action})>"
