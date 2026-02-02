"""
Partnership ORM Model
Links partners (users with partner role) to their restaurant/cafe (Place)
Allows a user to manage one or more places
"""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from services.catalog.src.models.base import Base


class PartnershipORM(Base):
    """Partnership database model - links partners to places"""
    __tablename__ = "partnerships"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    partner_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User ID of the partner (from auth service)"
    )

    place_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Place (restaurant/cafe) ID"
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manager",
        comment="Partner role at this place (manager, owner, etc)"
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        index=True,
        comment="Is this partnership active"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Indexes
    __table_args__ = (
        Index("idx_partnerships_partner_user", "partner_user_id"),
        Index("idx_partnerships_place", "place_id"),
        Index("idx_partnerships_partner_place", "partner_user_id", "place_id"),
        Index("idx_partnerships_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<PartnershipORM(partner={self.partner_user_id}, place={self.place_id})>"
