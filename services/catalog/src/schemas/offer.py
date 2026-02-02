from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ========== Response Schemas ==========

class MoneyOut(BaseModel):
    amount: Decimal
    currency: str


class OfferOut(BaseModel):
    """Public offer response for users and partners"""
    id: UUID
    place_id: UUID
    title: str
    description: str

    price: MoneyOut
    original_price: MoneyOut
    discount_percent: int

    quantity_total: int
    quantity_available: int

    pickup_start: datetime
    pickup_end: datetime

    status: str
    tags: list[str]
    allergens: list[str]
    image_urls: list[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OfferListOut(BaseModel):
    """Paginated list response"""
    offers: list[OfferOut]
    total: int
    limit: int
    offset: int


class ReservationOut(BaseModel):
    """Reservation confirmation"""
    offer_id: UUID
    quantity_reserved: int
    message: str


# ========== Request Schemas ==========

class OfferCreate(BaseModel):
    """Create new offer - partner only"""
    title: str = Field(..., min_length=3, max_length=120)
    description: str = Field(default="", max_length=2000)

    price_amount: Decimal = Field(..., gt=0, decimal_places=2)
    price_currency: str = Field(default="RUB", min_length=3, max_length=3)

    original_price_amount: Decimal = Field(..., gt=0, decimal_places=2)
    original_price_currency: str = Field(default="RUB", min_length=3, max_length=3)

    quantity_total: int = Field(..., gt=0)

    pickup_start: datetime
    pickup_end: datetime

    tags: list[str] = Field(default_factory=list)
    allergens: list[str] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)

    expires_at: Optional[datetime] = None

    @field_validator('price_currency', 'original_price_currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.upper()


class OfferUpdate(BaseModel):
    """Update existing offer - partner only (partial update)"""
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=2000)

    price_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    original_price_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)

    quantity_total: Optional[int] = Field(None, gt=0)

    pickup_start: Optional[datetime] = None
    pickup_end: Optional[datetime] = None

    tags: Optional[list[str]] = None
    allergens: Optional[list[str]] = None
    image_urls: Optional[list[str]] = None

    status: Optional[str] = None  # "active", "paused", "cancelled"


class OfferReserve(BaseModel):
    """Reserve quantity from an offer - user only"""
    quantity: int = Field(..., gt=0, description="Number of items to reserve")
