from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, Integer, DateTime, Enum, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from services.catalog.src.models.base import Base
from services.catalog.src.domain.offer import OfferStatus  # enum from domain


class OfferORM(Base):
    __tablename__ = "offers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    place_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Money (store as numeric + currency)
    price_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    price_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")

    original_price_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    original_price_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")

    quantity_total: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False)

    pickup_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pickup_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[OfferStatus] = mapped_column(
        Enum(OfferStatus, name="offer_status"),
        nullable=False,
        default=OfferStatus.DRAFT,
        index=True,
    )

    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    allergens: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    image_urls: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
