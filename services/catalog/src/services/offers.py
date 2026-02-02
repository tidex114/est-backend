"""
Offers service - business logic and use cases.
Orchestrates domain logic, repository operations, and validation.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from services.catalog.src.domain.offer import (
    Offer, Money, OfferStatus,
    ValidationError, NotAvailableError,
    utcnow
)
from services.catalog.src.repo.offers_repo import OffersRepo
from services.catalog.src.schemas.offer import OfferCreate, OfferUpdate


class OfferService:
    """
    Service layer for offer operations.
    Handles business use cases, transactions, and domain coordination.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = OffersRepo(db)

    # ========== Partner Operations ==========

    def create_offer(self, place_id: UUID, data: OfferCreate) -> Offer:
        """
        Create a new offer for a partner's place.

        Business rules:
        - Title must be unique per place (future enhancement)
        - Pickup window must be in the future
        - Price must be less than or equal to original price
        """
        now = utcnow()

        # Validate pickup times are in the future
        if data.pickup_start < now:
            raise ValidationError("Pickup start must be in the future")

        # Create domain entity (enforces all domain rules)
        offer = Offer.create(
            place_id=place_id,
            title=data.title,
            description=data.description,
            price=Money(data.price_amount, data.price_currency),
            original_price=Money(data.original_price_amount, data.original_price_currency),
            quantity_total=data.quantity_total,
            pickup_start=data.pickup_start,
            pickup_end=data.pickup_end,
            tags=data.tags,
            allergens=data.allergens,
            image_urls=data.image_urls,
        )

        if data.expires_at:
            offer.expires_at = data.expires_at

        # Save to database
        saved = self.repo.save(offer)
        self.db.commit()

        return saved

    def update_offer(self, offer_id: UUID, place_id: UUID, data: OfferUpdate) -> Offer:
        """
        Update an existing offer.

        Business rules:
        - Only the owner (partner) can update their offers
        - Cannot update cancelled or expired offers
        - Partial updates supported
        """
        offer = self.repo.get(offer_id)
        if not offer:
            raise NotAvailableError(f"Offer {offer_id} not found")

        # Authorization check: ensure partner owns this offer
        if offer.place_id != place_id:
            raise NotAvailableError("You don't have permission to update this offer")

        # Cannot edit cancelled/expired offers
        if offer.status in (OfferStatus.CANCELLED, OfferStatus.EXPIRED):
            raise NotAvailableError(f"Cannot edit offer in status {offer.status}")

        now = utcnow()

        # Apply updates (only fields that are provided)
        if data.title is not None:
            offer.title = data.title
        if data.description is not None:
            offer.description = data.description

        # Update pricing
        if data.price_amount is not None:
            offer.price = Money(data.price_amount, offer.price.currency)
        if data.original_price_amount is not None:
            offer.original_price = Money(data.original_price_amount, offer.original_price.currency)

        if data.quantity_total is not None:
            # Ensure we don't set total below what's already reserved
            reserved = offer.quantity_total - offer.quantity_available
            if data.quantity_total < reserved:
                raise ValidationError(f"Cannot set quantity_total below reserved amount ({reserved})")
            # Adjust available proportionally
            offer.quantity_available = data.quantity_total - reserved
            offer.quantity_total = data.quantity_total

        if data.pickup_start is not None:
            offer.pickup_start = data.pickup_start
        if data.pickup_end is not None:
            offer.pickup_end = data.pickup_end

        if data.tags is not None:
            offer.tags = data.tags
        if data.allergens is not None:
            offer.allergens = data.allergens
        if data.image_urls is not None:
            offer.image_urls = data.image_urls

        # Handle status changes
        if data.status is not None:
            if data.status == "active":
                offer.activate(now=now)
            elif data.status == "paused":
                offer.pause(now=now)
            elif data.status == "cancelled":
                offer.cancel(now=now)

        # Re-validate and save
        offer._validate()
        offer._touch(now)

        saved = self.repo.save(offer)
        self.db.commit()

        return saved

    def delete_offer(self, offer_id: UUID, place_id: UUID) -> bool:
        """
        Delete an offer (soft delete in future, hard delete for now).

        Business rules:
        - Only the owner can delete
        - Cannot delete if there are active reservations (future enhancement)
        """
        offer = self.repo.get(offer_id)
        if not offer:
            return False

        # Authorization check
        if offer.place_id != place_id:
            raise NotAvailableError("You don't have permission to delete this offer")

        # Check if there are reservations (quantity_available < quantity_total)
        reserved_qty = offer.quantity_total - offer.quantity_available
        if reserved_qty > 0:
            raise ValidationError(
                f"Cannot delete offer with active reservations ({reserved_qty} items reserved). "
                "Cancel the offer instead."
            )

        deleted = self.repo.delete(offer_id)
        self.db.commit()

        return deleted

    def get_partner_offers(
        self,
        place_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[Offer]:
        """Get all offers for a partner's place"""
        return self.repo.list_by_place(place_id, limit=limit, offset=offset)

    # ========== User Operations ==========

    def list_offers(
        self,
        limit: int = 50,
        offset: int = 0,
        active_only: bool = True
    ) -> list[Offer]:
        """
        List offers for customers.

        Business rules:
        - Only show ACTIVE offers by default
        - Refresh time-based statuses (expire old offers)
        - Sort by pickup_end (soonest first)
        """
        now = utcnow()
        offers = self.repo.list_active(now=now, limit=limit, offset=offset)

        # Refresh statuses and filter
        result = []
        for offer in offers:
            offer.refresh_time_status(now=now)
            if not active_only or offer.status == OfferStatus.ACTIVE:
                result.append(offer)

        # Save any status changes
        self.db.commit()

        return result

    def get_offer(self, offer_id: UUID) -> Offer | None:
        """Get a single offer by ID"""
        offer = self.repo.get(offer_id)
        if offer:
            now = utcnow()
            offer.refresh_time_status(now=now)
            self.db.commit()
        return offer

    def reserve_offer(self, offer_id: UUID, quantity: int, user_id: UUID) -> Offer:
        """
        Reserve quantity from an offer (for a user/customer).

        Business rules:
        - Offer must be ACTIVE
        - Must have sufficient quantity available
        - Offer must not be expired
        - Creates implicit reservation (in future, track in separate table)

        This is a simplified version. In production:
        - Create a Reservation entity with user_id, offer_id, quantity, status
        - Track reservation expiry (e.g., 15 minutes to complete payment)
        - Handle reservation release if payment fails
        """
        now = utcnow()

        offer = self.repo.get(offer_id)
        if not offer:
            raise NotAvailableError(f"Offer {offer_id} not found")

        # Domain logic handles all validation
        try:
            offer.reserve(quantity, now=now)
        except (ValidationError, NotAvailableError, InsufficientQuantityError) as e:
            raise  # Re-raise domain errors as-is

        # Save the updated offer
        saved = self.repo.save(offer)
        self.db.commit()

        return saved

    def count_offers(self) -> int:
        """Count total offers in system"""
        return self.repo.count_all()



