from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Iterable, Optional
from uuid import UUID, uuid4


# ---------- helpers ----------

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def ensure_tzaware(dt: datetime, field_name: str) -> datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError(f"{field_name} must be timezone-aware (UTC recommended)")
    return dt


def quantize_money(amount: Decimal) -> Decimal:
    # 2 decimals, classic money rounding
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------- domain errors ----------

class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class NotAvailableError(DomainError):
    pass


class InsufficientQuantityError(DomainError):
    pass


# ---------- value objects ----------

@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "RUB"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("Money.amount must be Decimal")
        if self.amount < Decimal("0"):
            raise ValidationError("Money.amount cannot be negative")
        if not self.currency or len(self.currency) not in (3,):
            raise ValidationError("Money.currency must be a 3-letter code like 'RUB'")
        object.__setattr__(self, "amount", quantize_money(self.amount))
        object.__setattr__(self, "currency", self.currency.upper())

    def __add__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        if self.amount < other.amount:
            raise ValidationError("Money subtraction would go negative")
        return Money(self.amount - other.amount, self.currency)

    def _assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValidationError("Money currency mismatch")


class OfferStatus(str, Enum):
    DRAFT = "draft"          # created but not visible
    ACTIVE = "active"        # visible and reservable
    PAUSED = "paused"        # temporarily hidden/unavailable
    SOLD_OUT = "sold_out"    # no quantity left
    EXPIRED = "expired"      # pickup window ended
    CANCELLED = "cancelled"  # removed by place/admin


# ---------- domain entity ----------

@dataclass(slots=True)
class Offer:
    """
    Offer = a purchasable listing from a place with a pickup window and limited quantity.

    Domain rules live here (invariants), NOT in API/DB.
    """
    id: UUID
    place_id: UUID

    title: str
    description: str = ""

    # pricing
    original_price: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    price: Money = field(default_factory=lambda: Money(Decimal("0.00")))

    # inventory
    quantity_total: int = 1
    quantity_available: int = 1

    # pickup window (timezone-aware)
    pickup_start: datetime = field(default_factory=utcnow)
    pickup_end: datetime = field(default_factory=utcnow)

    # metadata
    status: OfferStatus = OfferStatus.DRAFT
    tags: list[str] = field(default_factory=list)          # e.g. ["bakery", "vegan"]
    allergens: list[str] = field(default_factory=list)     # e.g. ["nuts", "gluten"]
    image_urls: list[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    # optional: if you want to auto-expire earlier than pickup_end
    expires_at: Optional[datetime] = None

    # ----- constructors -----

    @staticmethod
    def create(
        *,
        place_id: UUID,
        title: str,
        price: Money,
        original_price: Money,
        quantity_total: int,
        pickup_start: datetime,
        pickup_end: datetime,
        description: str = "",
        tags: Optional[Iterable[str]] = None,
        allergens: Optional[Iterable[str]] = None,
        image_urls: Optional[Iterable[str]] = None,
        currency_must_match: bool = True,
    ) -> "Offer":
        offer = Offer(
            id=uuid4(),
            place_id=place_id,
            title=title.strip(),
            description=description.strip(),
            price=price,
            original_price=original_price,
            quantity_total=quantity_total,
            quantity_available=quantity_total,
            pickup_start=pickup_start,
            pickup_end=pickup_end,
            tags=list(tags or []),
            allergens=list(allergens or []),
            image_urls=list(image_urls or []),
            status=OfferStatus.DRAFT,
        )
        if currency_must_match and offer.price.currency != offer.original_price.currency:
            raise ValidationError("price and original_price currency must match")
        offer._validate()
        return offer

    # ----- domain behavior -----

    def activate(self, *, now: Optional[datetime] = None) -> None:
        self._validate()
        if self.status in (OfferStatus.CANCELLED, OfferStatus.EXPIRED):
            raise NotAvailableError(f"Cannot activate offer in status={self.status}")
        self.status = OfferStatus.ACTIVE
        self._touch(now)

    def pause(self, *, now: Optional[datetime] = None) -> None:
        if self.status == OfferStatus.ACTIVE:
            self.status = OfferStatus.PAUSED
            self._touch(now)

    def cancel(self, *, now: Optional[datetime] = None) -> None:
        self.status = OfferStatus.CANCELLED
        self._touch(now)

    def is_in_pickup_window(self, now: datetime) -> bool:
        now = ensure_tzaware(now, "now")
        return self.pickup_start <= now <= self.pickup_end

    def is_expired(self, now: datetime) -> bool:
        now = ensure_tzaware(now, "now")
        if self.expires_at is not None:
            return now > self.expires_at
        return now > self.pickup_end

    def refresh_time_status(self, *, now: datetime) -> None:
        """
        Call this when reading/serving offers (or via a scheduled job later).
        """
        now = ensure_tzaware(now, "now")
        if self.status not in (OfferStatus.CANCELLED, OfferStatus.SOLD_OUT):
            if self.is_expired(now):
                self.status = OfferStatus.EXPIRED
                self._touch(now)

    def can_reserve(self, qty: int, now: datetime) -> bool:
        now = ensure_tzaware(now, "now")
        if qty <= 0:
            return False
        if self.status != OfferStatus.ACTIVE:
            return False
        if self.is_expired(now):
            return False
        # You may choose: allow reserve only before pickup_end (even if pickup_start not reached)
        # This allows pre-ordering for a pickup window later today.
        if now > self.pickup_end:
            return False
        return self.quantity_available >= qty

    def reserve(self, qty: int, *, now: datetime) -> None:
        now = ensure_tzaware(now, "now")
        self.refresh_time_status(now=now)

        if qty <= 0:
            raise ValidationError("qty must be > 0")
        if self.status != OfferStatus.ACTIVE:
            raise NotAvailableError(f"Offer is not active (status={self.status})")
        if self.is_expired(now):
            raise NotAvailableError("Offer is expired")
        if self.quantity_available < qty:
            raise InsufficientQuantityError("Not enough quantity available")

        self.quantity_available -= qty
        if self.quantity_available == 0:
            self.status = OfferStatus.SOLD_OUT
        self._touch(now)

    def release(self, qty: int, *, now: datetime) -> None:
        """
        Used if an order was cancelled / payment failed etc.
        """
        now = ensure_tzaware(now, "now")

        if qty <= 0:
            raise ValidationError("qty must be > 0")
        if self.status in (OfferStatus.CANCELLED, OfferStatus.EXPIRED):
            raise NotAvailableError(f"Cannot release into status={self.status}")

        self.quantity_available = min(self.quantity_total, self.quantity_available + qty)

        # If it was sold out and now we have stock again, return to ACTIVE (if not paused)
        if self.status == OfferStatus.SOLD_OUT and self.quantity_available > 0:
            self.status = OfferStatus.ACTIVE

        self._touch(now)

    def discount_percent(self) -> int:
        """
        Returns integer discount percent vs original price (0..100).
        """
        if self.original_price.amount == Decimal("0.00"):
            return 0
        if self.price.amount >= self.original_price.amount:
            return 0
        ratio = (Decimal("1") - (self.price.amount / self.original_price.amount)) * Decimal("100")
        # round to nearest int
        return int(ratio.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    # ----- internal -----

    def _touch(self, now: Optional[datetime] = None) -> None:
        self.updated_at = ensure_tzaware(now or utcnow(), "now")

    def _validate(self) -> None:
        if not isinstance(self.id, UUID):
            raise ValidationError("id must be UUID")
        if not isinstance(self.place_id, UUID):
            raise ValidationError("place_id must be UUID")

        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("title must be at least 3 characters")
        if len(self.title) > 120:
            raise ValidationError("title is too long (max 120)")
        if len(self.description) > 2000:
            raise ValidationError("description is too long (max 2000)")

        if self.quantity_total <= 0:
            raise ValidationError("quantity_total must be > 0")
        if not (0 <= self.quantity_available <= self.quantity_total):
            raise ValidationError("quantity_available must be between 0 and quantity_total")

        self.pickup_start = ensure_tzaware(self.pickup_start, "pickup_start")
        self.pickup_end = ensure_tzaware(self.pickup_end, "pickup_end")
        if self.pickup_end <= self.pickup_start:
            raise ValidationError("pickup_end must be after pickup_start")

        if self.expires_at is not None:
            self.expires_at = ensure_tzaware(self.expires_at, "expires_at")
            if self.expires_at < self.pickup_start:
                raise ValidationError("expires_at cannot be before pickup_start")

        # price rules
        if self.price.amount <= Decimal("0.00"):
            raise ValidationError("price must be > 0")
        if self.original_price.amount <= Decimal("0.00"):
            raise ValidationError("original_price must be > 0")
        if self.price.currency != self.original_price.currency:
            raise ValidationError("price and original_price currency must match")
        if self.price.amount > self.original_price.amount:
            # optional: allow equal, but not higher
            raise ValidationError("price cannot be higher than original_price")

        # normalize lists
        self.tags = [t.strip().lower() for t in self.tags if t and t.strip()]
        self.allergens = [a.strip().lower() for a in self.allergens if a and a.strip()]
        self.image_urls = [u.strip() for u in self.image_urls if u and u.strip()]

        # timestamps
        self.created_at = ensure_tzaware(self.created_at, "created_at")
        self.updated_at = ensure_tzaware(self.updated_at, "updated_at")
