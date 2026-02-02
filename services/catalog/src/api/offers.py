"""
Offers API endpoints.
Handles HTTP layer: request validation, response formatting, error handling.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Path, status

from services.catalog.src.core.dependencies import (
    DBSession, PartnerUser, CustomerUser, AuthUser
)
from services.catalog.src.services.offers import OfferService
from services.catalog.src.schemas.offer import (
    OfferOut, OfferCreate, OfferUpdate, OfferReserve,
    OfferListOut, ReservationOut, MoneyOut
)
from services.catalog.src.domain.offer import (
    DomainError, ValidationError, NotAvailableError, InsufficientQuantityError
)


router = APIRouter(prefix="/offers", tags=["offers"])


def domain_to_schema(offer) -> OfferOut:
    """Convert domain Offer to API schema OfferOut"""
    return OfferOut(
        id=offer.id,
        place_id=offer.place_id,
        title=offer.title,
        description=offer.description,
        price=MoneyOut(amount=offer.price.amount, currency=offer.price.currency),
        original_price=MoneyOut(
            amount=offer.original_price.amount,
            currency=offer.original_price.currency
        ),
        discount_percent=offer.discount_percent(),
        quantity_total=offer.quantity_total,
        quantity_available=offer.quantity_available,
        pickup_start=offer.pickup_start,
        pickup_end=offer.pickup_end,
        status=offer.status.value,
        tags=offer.tags,
        allergens=offer.allergens,
        image_urls=offer.image_urls,
        created_at=offer.created_at,
        updated_at=offer.updated_at,
    )


# ========== USER ENDPOINTS (Customers) ==========

@router.get(
    "",
    response_model=OfferListOut,
    summary="List offers",
    description="Get list of available offers for customers. Shows only ACTIVE offers by default.",
)
def list_offers(
    db: DBSession,
    user: CustomerUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    active_only: Annotated[bool, Query()] = True,
):
    """
    **User Role Required**

    List all available offers with pagination.
    - Only ACTIVE offers are shown by default
    - Sorted by pickup_end (soonest expiring first)
    - Expired offers are automatically filtered out
    """
    try:
        service = OfferService(db)
        offers = service.list_offers(limit=limit, offset=offset, active_only=active_only)
        total = service.count_offers()

        return OfferListOut(
            offers=[domain_to_schema(o) for o in offers],
            total=total,
            limit=limit,
            offset=offset,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{offer_id}",
    response_model=OfferOut,
    summary="Get offer details",
    description="Get detailed information about a specific offer",
)
def get_offer(
    offer_id: Annotated[UUID, Path()],
    db: DBSession,
    user: AuthUser,  # Any authenticated user can view
):
    """
    **Authentication Required**

    Get full details of a specific offer by ID.
    """
    service = OfferService(db)
    offer = service.get_offer(offer_id)

    if not offer:
        raise HTTPException(status_code=404, detail=f"Offer {offer_id} not found")

    return domain_to_schema(offer)


@router.post(
    "/{offer_id}/reserve",
    response_model=ReservationOut,
    status_code=status.HTTP_200_OK,
    summary="Reserve offer",
    description="Reserve a quantity of items from an offer",
)
def reserve_offer(
    offer_id: Annotated[UUID, Path()],
    data: OfferReserve,
    db: DBSession,
    user: CustomerUser,
):
    """
    **User Role Required**

    Reserve a quantity from an offer. This reduces the available quantity.

    Business Rules:
    - Offer must be ACTIVE
    - Must have sufficient quantity available
    - Offer must not be expired

    In production, this would:
    1. Create a Reservation record with expiry time (e.g., 15 minutes)
    2. Link reservation to user's cart/order
    3. Release reservation if payment not completed in time
    """
    try:
        service = OfferService(db)
        offer = service.reserve_offer(offer_id, data.quantity, user.user_id)

        return ReservationOut(
            offer_id=offer.id,
            quantity_reserved=data.quantity,
            message=f"Successfully reserved {data.quantity} item(s). "
                    f"{offer.quantity_available} remaining."
        )
    except NotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientQuantityError as e:
        raise HTTPException(status_code=409, detail=str(e))  # Conflict
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== PARTNER ENDPOINTS ==========

@router.post(
    "",
    response_model=OfferOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create offer",
    description="Create a new offer (partners only)",
)
def create_offer(
    data: OfferCreate,
    db: DBSession,
    partner: PartnerUser,
):
    """
    **Partner Role Required**

    Create a new food offer for your place.

    The offer is created in DRAFT status by default.
    Update it to "active" status to make it visible to customers.
    """
    try:
        service = OfferService(db)
        offer = service.create_offer(partner.place_id, data)

        return domain_to_schema(offer)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{offer_id}",
    response_model=OfferOut,
    summary="Update offer",
    description="Update an existing offer (partners only)",
)
def update_offer(
    offer_id: Annotated[UUID, Path()],
    data: OfferUpdate,
    db: DBSession,
    partner: PartnerUser,
):
    """
    **Partner Role Required**

    Update an existing offer. Only the owner can update their offers.

    Partial updates are supported - only provide fields you want to change.

    Cannot update cancelled or expired offers.
    """
    try:
        service = OfferService(db)
        offer = service.update_offer(offer_id, partner.place_id, data)

        return domain_to_schema(offer)
    except NotAvailableError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{offer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete offer",
    description="Delete an offer (partners only)",
)
def delete_offer(
    offer_id: Annotated[UUID, Path()],
    db: DBSession,
    partner: PartnerUser,
):
    """
    **Partner Role Required**

    Delete an offer. Only the owner can delete their offers.

    Cannot delete offers with active reservations - cancel them instead.
    """
    try:
        service = OfferService(db)
        deleted = service.delete_offer(offer_id, partner.place_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Offer {offer_id} not found")

        return None  # 204 No Content
    except NotAvailableError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/partner/my-offers",
    response_model=OfferListOut,
    summary="Get my offers",
    description="Get all offers for the authenticated partner's place",
)
def get_my_offers(
    db: DBSession,
    partner: PartnerUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    **Partner Role Required**

    Get all offers for your place (dashboard view).
    Shows offers in all statuses (draft, active, paused, etc.)
    """
    try:
        service = OfferService(db)
        offers = service.get_partner_offers(partner.place_id, limit=limit, offset=offset)
        total = len(offers)  # Simple count; improve with dedicated query

        return OfferListOut(
            offers=[domain_to_schema(o) for o in offers],
            total=total,
            limit=limit,
            offset=offset,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

