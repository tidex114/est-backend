from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.catalog.src.domain.offer import Offer, Money
from services.catalog.src.models.offer import OfferORM


def _to_domain(o: OfferORM) -> Offer:
    return Offer(
        id=UUID(str(o.id)) if isinstance(o.id, str) else o.id,
        place_id=UUID(str(o.place_id)) if isinstance(o.place_id, str) else o.place_id,
        title=o.title,
        description=o.description,
        price=Money(Decimal(str(o.price_amount)), o.price_currency),
        original_price=Money(Decimal(str(o.original_price_amount)), o.original_price_currency),
        quantity_total=o.quantity_total,
        quantity_available=o.quantity_available,
        pickup_start=o.pickup_start,
        pickup_end=o.pickup_end,
        expires_at=o.expires_at,
        status=o.status,
        tags=list(o.tags or []),
        allergens=list(o.allergens or []),
        image_urls=list(o.image_urls or []),
        created_at=o.created_at,
        updated_at=o.updated_at,
    )


def _apply_domain(o: OfferORM, d: Offer) -> None:
    o.place_id = d.place_id
    o.title = d.title
    o.description = d.description

    o.price_amount = d.price.amount
    o.price_currency = d.price.currency
    o.original_price_amount = d.original_price.amount
    o.original_price_currency = d.original_price.currency

    o.quantity_total = d.quantity_total
    o.quantity_available = d.quantity_available

    o.pickup_start = d.pickup_start
    o.pickup_end = d.pickup_end
    o.expires_at = d.expires_at

    o.status = d.status
    o.tags = list(d.tags)
    o.allergens = list(d.allergens)
    o.image_urls = list(d.image_urls)

    o.created_at = d.created_at
    o.updated_at = d.updated_at


class OffersRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_active(self, *, now: datetime, limit: int = 50, offset: int = 0) -> list[Offer]:
        stmt = (
            select(OfferORM)
            .order_by(OfferORM.pickup_end.asc())
            .limit(limit)
            .offset(offset)
        )
        rows = self.db.execute(stmt).scalars().all()
        return [_to_domain(r) for r in rows]

    def list_by_place(self, place_id: UUID, *, limit: int = 50, offset: int = 0) -> list[Offer]:
        """Get all offers for a specific place (for partner dashboard)"""
        stmt = (
            select(OfferORM)
            .where(OfferORM.place_id == place_id)
            .order_by(OfferORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = self.db.execute(stmt).scalars().all()
        return [_to_domain(r) for r in rows]

    def count_all(self) -> int:
        """Count all offers"""
        from sqlalchemy import func
        return self.db.query(func.count(OfferORM.id)).scalar() or 0

    def get(self, offer_id: UUID) -> Offer | None:
        row = self.db.get(OfferORM, offer_id)
        return _to_domain(row) if row else None

    def save(self, offer: Offer) -> Offer:
        row = self.db.get(OfferORM, offer.id)
        if row is None:
            row = OfferORM(id=offer.id)
            self.db.add(row)
        _apply_domain(row, offer)
        self.db.flush()
        return _to_domain(row)
    def delete(self, offer_id: UUID) -> bool:
        """Delete an offer by ID. Returns True if deleted, False if not found."""
        row = self.db.get(OfferORM, offer_id)
        if row is None:
            return False
        self.db.delete(row)
        self.db.flush()
        return True
