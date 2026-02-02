# EST Catalog Service - Offers API

Complete implementation of the offers management system with role-based access control.

## 🚀 Features Implemented

### ✅ Partner Endpoints (Restaurant Owners)
1. **Create Offer** - `POST /offers`
   - Create new food offers with pricing, quantity, and pickup windows
   - Automatic validation of business rules
   - Created in DRAFT status by default

2. **Update Offer** - `PATCH /offers/{offer_id}`
   - Partial updates supported
   - Activate/pause/cancel offers
   - Adjust pricing and quantities
   - Only owner can update

3. **Delete Offer** - `DELETE /offers/{offer_id}`
   - Hard delete (soft delete in future)
   - Cannot delete with active reservations
   - Only owner can delete

4. **Get My Offers** - `GET /offers/partner/my-offers`
   - Dashboard view of all partner's offers
   - All statuses included (draft, active, paused, etc.)

### ✅ User Endpoints (Customers)
1. **List Offers** - `GET /offers`
   - Browse available offers
   - Only ACTIVE offers shown by default
   - Pagination support
   - Auto-expire old offers

2. **Get Offer Details** - `GET /offers/{offer_id}`
   - View full details of specific offer
   - Includes discount percentage
   - Shows availability

3. **Reserve Offer** - `POST /offers/{offer_id}/reserve`
   - Reserve quantity from offer
   - Reduces available quantity
   - Validates availability and expiry

## 📁 Architecture

```
services/catalog/src/
├── api/                    # HTTP endpoints (FastAPI routes)
│   └── offers.py          # All 6 endpoints with role checks
├── schemas/               # API request/response models
│   └── offer.py          # Pydantic models for validation
├── services/              # Business logic layer
│   └── offers.py         # OfferService with use cases
├── domain/                # Core business rules
│   └── offer.py          # Offer entity with behavior
├── repo/                  # Data access layer
│   └── offers_repo.py    # Database operations
├── models/                # Database schema
│   └── offer.py          # SQLAlchemy ORM models
├── core/                  # Infrastructure
│   ├── db.py             # Database connection
│   ├── settings.py       # Configuration
│   └── dependencies.py   # DI and auth helpers
└── main.py                # FastAPI application
```

## 🔐 Authentication

Currently using **header-based auth** for development:

```http
X-User-Id: {uuid}          # User's unique ID
X-User-Role: user|partner  # Role: "user" or "partner"
X-Place-Id: {uuid}         # Required for partners only
```

### Production TODO:
- Implement JWT token authentication
- Replace headers with `Authorization: Bearer <token>`
- Add token validation middleware
- Implement refresh tokens

## 🎯 API Endpoints Summary

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/offers` | user | List active offers |
| `GET` | `/offers/{id}` | any | Get offer details |
| `POST` | `/offers/{id}/reserve` | user | Reserve quantity |
| `POST` | `/offers` | partner | Create new offer |
| `PATCH` | `/offers/{id}` | partner | Update offer |
| `DELETE` | `/offers/{id}` | partner | Delete offer |
| `GET` | `/offers/partner/my-offers` | partner | Get partner's offers |

## 🧪 Testing

### 1. Start the application:
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run migrations
alembic upgrade head

# Start server
uvicorn services.catalog.src.main:app --reload
```

### 2. Test with curl or HTTP client:

See `API_EXAMPLES.http` for complete examples.

**Quick test - Create offer as partner:**
```bash
curl -X POST http://localhost:8000/offers \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 550e8400-e29b-41d4-a716-446655440000" \
  -H "X-User-Role: partner" \
  -H "X-Place-Id: 123e4567-e89b-12d3-a456-426614174000" \
  -d '{
    "title": "Breakfast Combo",
    "price_amount": 299.00,
    "original_price_amount": 499.00,
    "quantity_total": 20,
    "pickup_start": "2026-01-27T08:00:00+03:00",
    "pickup_end": "2026-01-27T12:00:00+03:00"
  }'
```

## 📊 Domain Model

### Offer Entity
- **Identity**: `UUID` (unique identifier)
- **Ownership**: `place_id` (restaurant/place)
- **Content**: `title`, `description`, `image_urls`
- **Pricing**: `price`, `original_price` (Money value objects)
- **Inventory**: `quantity_total`, `quantity_available`
- **Schedule**: `pickup_start`, `pickup_end`, `expires_at`
- **Status**: `draft`, `active`, `paused`, `sold_out`, `expired`, `cancelled`
- **Metadata**: `tags`, `allergens`, `created_at`, `updated_at`

### Business Rules (enforced in domain layer)
- ✅ Price must be ≤ original price
- ✅ Title: 3-120 characters
- ✅ Quantity available ≤ quantity total
- ✅ Pickup end must be after pickup start
- ✅ Cannot activate cancelled/expired offers
- ✅ Cannot reserve from non-active offers
- ✅ Auto-transition to SOLD_OUT when quantity reaches 0
- ✅ Auto-transition to EXPIRED after pickup window

## 🔄 Data Flow Example

**Reserve Offer Flow:**

```
1. User Request:
   POST /offers/{id}/reserve
   Headers: X-User-Id, X-User-Role: user
   Body: {"quantity": 2}
   
2. API Layer (offers.py):
   - Validates authentication (require_user)
   - Validates request schema (OfferReserve)
   - Calls service layer
   
3. Service Layer (OfferService):
   - Fetches offer from repository
   - Calls domain method: offer.reserve(qty)
   - Handles transaction
   - Returns updated offer
   
4. Domain Layer (Offer.reserve):
   - Validates: status == ACTIVE
   - Validates: not expired
   - Validates: sufficient quantity
   - Updates: quantity_available -= qty
   - Auto-transition to SOLD_OUT if needed
   
5. Repository Layer:
   - Converts domain Offer → OfferORM
   - Saves to database
   - Returns domain Offer
   
6. API Response:
   - Converts domain → OfferOut schema
   - Returns JSON with reservation confirmation
```

## 🛡️ Error Handling

All domain errors are caught and converted to appropriate HTTP status codes:

- `ValidationError` → 400 Bad Request
- `NotAvailableError` → 404 Not Found or 403 Forbidden
- `InsufficientQuantityError` → 409 Conflict
- General errors → 500 Internal Server Error

## 📈 Future Enhancements

### Short-term:
- [ ] Add filtering (by tags, price range, distance)
- [ ] Add sorting options (price, discount, pickup time)
- [ ] Implement proper reservation tracking (separate table)
- [ ] Add reservation expiry (auto-release after N minutes)

### Medium-term:
- [ ] Implement JWT authentication
- [ ] Add image upload support
- [ ] Implement soft delete (keep history)
- [ ] Add offer statistics (views, reservations)
- [ ] Implement search functionality

### Long-term:
- [ ] Add geolocation-based filtering
- [ ] Implement real-time notifications (WebSocket)
- [ ] Add caching layer (Redis)
- [ ] Implement event sourcing for audit trail
- [ ] Add recommendation engine

## 🧰 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Architecture**: Layered/Onion Architecture

## 📝 Notes

This is a **production-ready foundation** with:
- ✅ Proper separation of concerns
- ✅ Domain-driven design principles
- ✅ Role-based access control
- ✅ Comprehensive validation
- ✅ Transaction management
- ✅ Error handling
- ✅ Type safety

The code is ready to:
- Scale to multiple services
- Add new features without breaking existing code
- Support multiple developers working in parallel
- Migrate to microservices architecture when needed
