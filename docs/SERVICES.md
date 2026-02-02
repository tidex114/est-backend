"""
Services Documentation - EST Backend

Detailed information about each service and the shared infrastructure.

## Services Overview

EST Backend consists of 3 main components:
1. **Auth Service** - Authentication and user management
2. **Catalog Service** - Offer management and reservations
3. **Shared Infrastructure** - Common utilities

---

## Auth Service

**Location**: `services/auth/`
**Port**: 8001
**Database**: `est_auth`

### Responsibility

Handles all user authentication, registration, email verification, and token management.

### Structure

```
services/auth/src/
├── core/
│   ├── settings.py          # Configuration
│   ├── db.py                # Database engine
│   ├── dependencies.py       # FastAPI dependencies
│   ├── jwt_utils.py          # JWT encoding/decoding
│   └── email_service.py      # Email handling
├── domain/
│   └── user.py              # User aggregate, value objects, domain logic
├── models/
│   ├── user.py              # UserORM
│   └── verification_token.py # VerificationTokenORM
├── repo/
│   ├── __init__.py          # UserRepository
│   └── verification_token.py # VerificationTokenRepository
├── schemas/
│   └── __init__.py          # Request/response models
├── services/
│   └── __init__.py          # AuthService (business logic)
├── api/
│   ├── __init__.py          # Router imports
│   └── auth.py              # Endpoint definitions
└── main.py                  # FastAPI app

alembic/
└── versions/
    └── create_auth_tables.py # Database migrations
```

### Key Components

#### Core Layer
- **settings.py** - JWT configuration, email settings, database URL
- **jwt_utils.py** - Token encoding/decoding with HS256
- **email_service.py** - Mock (dev) and SMTP (prod) email sending
- **dependencies.py** - FastAPI dependency injection for authentication

#### Domain Layer
- **User aggregate** - Entity with business logic for creation and verification
- **Email value object** - Email validation
- **Password value object** - Password strength validation and bcrypt hashing
- **VerificationToken aggregate** - Single-use email verification tokens
- **Domain errors** - InvalidEmail, WeakPassword, UserExists, InvalidCredentials, etc.

#### Database
- **users table** - User accounts with email, password_hash, role, is_verified
- **verification_tokens table** - One-time use tokens with expiry

### Endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | /auth/register | Create account | ❌ |
| POST | /auth/login | Authenticate | ❌ |
| POST | /auth/verify-email | Confirm email | ❌ |
| POST | /auth/refresh-token | Get new token | ❌ |
| GET | /auth/me | Current user | ✅ |
| GET | /health | Health check | ❌ |
| GET | /db/health | DB health check | ❌ |

### Key Features

✅ **User Registration**
- Email validation
- Password strength requirements (8+ chars, uppercase, lowercase, digit)
- Automatic verification email sending
- Email verification with single-use tokens

✅ **Authentication**
- Login with email/password
- JWT access tokens (15 min expiry)
- Refresh tokens (7 day expiry)
- Token refresh mechanism

✅ **Security**
- Bcrypt password hashing
- Email verification prevents fake accounts
- Single-use verification tokens
- JWT signature validation

✅ **Role Management**
- User role types: "user" (customer), "partner", "admin"
- Roles included in JWT claims
- Used for authorization in other services

### Example Flow

```
1. Client: POST /auth/register {email, password, role}
2. API: Validate input with Pydantic
3. Service: Call domain to create user
4. Domain: Validate email, password, role
5. Repository: Save to database
6. Service: Create verification token and send email
7. API: Return 201 with user data
8. Client: Check email for verification link
9. Client: POST /auth/verify-email {token}
10. Service: Verify token and mark user as verified
11. Client: POST /auth/login {email, password}
12. Service: Verify credentials and generate tokens
13. Client: Use access_token for other services
```

---

## Catalog Service

**Location**: `services/catalog/`
**Port**: 8000
**Database**: `est_catalog`

### Responsibility

Manages food offers, reservations, and user activity tracking.

### Structure

```
services/catalog/src/
├── core/
│   ├── settings.py          # Configuration
│   ├── db.py                # Database engine
│   ├── dependencies.py       # FastAPI dependencies (updated)
│   └── ...
├── domain/
│   └── offer.py             # Offer aggregate, business logic
├── models/
│   ├── offer.py             # OfferORM
│   ├── user_history.py      # UserHistoryORM (new)
│   └── partnership.py        # PartnershipORM (new)
├── repo/
│   ├── offers_repo.py        # OfferRepository
│   └── ...
├── schemas/
│   └── offer.py             # Offer request/response models
├── services/
│   └── offers.py            # OfferService
├── api/
│   └── offers.py            # Offer endpoints
└── main.py                  # FastAPI app

alembic/
└── versions/
    ├── d843b5f4a9c6_create_offers.py  # Original
    └── create_user_history_partnership.py # New (user_history, partnerships)
```

### Key Components

#### New Models (Added)
- **UserHistoryORM** - Tracks user actions (OFFER_VIEWED, OFFER_RESERVED, etc.)
- **PartnershipORM** - Links partners to places they manage

#### Updated Components
- **dependencies.py** - Enhanced with AdminUser role, email field in CurrentUser
- **models/offer.py** - Unchanged, includes offer management

#### Database
- **offers table** - Food offers with pricing, quantity, status, time windows
- **user_history table** - Action log for analytics (future)
- **partnerships table** - Partner-place relationships

### Endpoints

| Method | Path | Purpose | Role |
|--------|------|---------|------|
| GET | /offers | List all offers | any |
| GET | /offers/{id} | Get offer details | any |
| POST | /offers | Create offer | partner |
| PATCH | /offers/{id} | Update offer | partner |
| DELETE | /offers/{id} | Delete offer | partner |
| POST | /offers/{id}/reserve | Reserve items | user |
| GET | /health | Health check | any |

### Key Features

✅ **Offer Management**
- Partners create, edit, delete offers
- Customers browse and reserve
- Quantity tracking
- Status management (draft, active, paused, expired)
- Discount calculations
- Image and allergen tracking

✅ **Role-Based Access**
- Customers can only browse and reserve
- Partners can only manage own offers
- Admin can manage all offers (future)

✅ **Data Structure**
- User history foundation (structure ready, impl. future)
- Partnership tracking for partner-place relationships
- Proper indexing for query performance

### Example Flow

```
Partner:
1. Partner logs in via Auth service
2. POST /offers with offer details
3. API checks partner role
4. Service validates business rules
5. Repository saves to database
6. Response: 201 Created with offer_id

Customer:
1. Customer logs in via Auth service
2. GET /offers to list all offers
3. API returns list of active offers
4. Customer selects offer
5. POST /offers/{id}/reserve {quantity}
6. Service checks availability
7. Response: 200 OK with reservation confirmation
```

---

## Shared Infrastructure

**Location**: `services/shared/`

### Components

#### exceptions.py
Standardized exception definitions used across services.

```python
- ServiceError (base)
- ValidationError
- AuthenticationError
- AuthorizationError
- NotFoundError
- ConflictError
- ExternalServiceError
```

#### http_client.py
HTTP client for service-to-service communication.

```python
ServiceHTTPClient:
  - get() - GET requests
  - post() - POST requests
  - validate_token() - Call auth service to validate JWT
```

#### settings.py
Shared configuration.

```
- auth_service_url
- catalog_service_url
- service_call_timeout
- env (dev/staging/prod)
```

### Usage

```python
# In catalog service to validate tokens with auth service
from services.shared.http_client import ServiceHTTPClient
from services.shared.settings import shared_settings

client = ServiceHTTPClient(shared_settings.auth_service_url)
claims = client.validate_token(token)
# Returns: {user_id, email, role, iat, exp}
```

---

## Inter-Service Communication

Services communicate via HTTP (future: message queue for async operations).

### Current Communication

**Catalog → Auth** (for token validation):
- URL: `{AUTH_SERVICE_URL}/auth/validate?token={jwt}`
- Request: GET with Authorization header
- Response: JWT claims (user_id, email, role)
- Error: 401 if invalid/expired

### Future Communication

- Order service → Catalog (check offer availability)
- Order service → Payment service (process payments)
- Notification service → Auth (send password reset emails)
- All services → Message queue (async event processing)

---

## Database Relationship

```
est_auth (Auth Service)
├── users
│   ├── id (UUID)
│   ├── email
│   ├── password_hash
│   ├── role
│   ├── is_verified
│   └── timestamps
└── verification_tokens
    ├── token
    ├── user_id (FK → users.id)
    └── expiry info

est_catalog (Catalog Service)
├── offers
│   ├── id (UUID)
│   ├── place_id
│   ├── pricing & quantity
│   └── status & timestamps
├── user_history
│   ├── id (UUID)
│   ├── user_id (from auth service)
│   ├── offer_id (FK → offers.id)
│   ├── action
│   └── timestamp
└── partnerships
    ├── id (UUID)
    ├── partner_user_id (from auth service)
    ├── place_id
    └── role & status
```

**Key**: Services don't share databases. User IDs are UUIDs from auth service, referenced in catalog.

---

## Adding a New Service

To add a new service, follow the same pattern:

1. **Create service folder**: `services/myservice/src/`
2. **Implement 7 layers**: core, domain, models, repo, schemas, services, api
3. **Create migrations**: `services/myservice/alembic/`
4. **Add configuration**: `services/myservice/src/core/settings.py`
5. **Define endpoints**: `services/myservice/src/api/`
6. **Add to shared**: Update shared infrastructure if needed

Example: Order Service
```
services/order/src/
├── core/ (config, db, deps, payments client)
├── domain/ (Order aggregate, OrderItem, business rules)
├── models/ (OrderORM, OrderItemORM)
├── repo/ (OrderRepository)
├── schemas/ (OrderCreate, OrderOut, etc.)
├── services/ (OrderService - orchestrate order creation, payment, notification)
└── api/ (Order endpoints)
```

---

For API details, see [API_REFERENCE.md](./API_REFERENCE.md)

For architecture details, see [ARCHITECTURE.md](./ARCHITECTURE.md)
