"""
EST Backend Architecture

System design, layering philosophy, and how everything connects.

## System Overview

EST is a service-oriented backend for a platform where users buy fresh food at lower prices.

**Services**:
- **Auth Service** (port 8001) - User registration, login, email verification, JWT tokens
- **Catalog Service** (port 8000) - Offer management, reservations, user activity
- **Shared Infrastructure** - Common utilities for inter-service communication

**Database**:
- PostgreSQL (separate database per service: est_auth, est_catalog)

## 7-Layer Architecture

Each service follows the same proven architecture for consistency and maintainability:

```
Layer 7: API           → HTTP endpoints, routing, error response formatting
Layer 6: Services      → Business use cases, orchestration, transactions
Layer 5: Schemas       → Request/response models, Pydantic validation
Layer 4: Repository    → Data persistence, database queries
Layer 3: Models        → ORM definitions, database schema
Layer 2: Domain        → Business logic (zero infrastructure dependencies)
Layer 1: Core          → Configuration, database, JWT, email, dependencies
```

### Why This Structure?

**Testability**: Each layer can be tested independently. Domain logic has no dependencies.

**Maintainability**: Clear separation of concerns. Each layer has one responsibility.

**Scalability**: Easy to extend without breaking existing code. New features follow the same pattern.

**Reusability**: Layers can be reused across services. Same pattern for all services.

## Data Flow Example: User Registration

```
1. Client: POST /auth/register {email, password, role}
   ↓
2. API Layer: Validates request schema via Pydantic
   ↓
3. Service Layer: AuthService.register()
   - Calls domain: User.create(email, password, role)
   - Domain validates email, password strength
   - Raises InvalidEmail, WeakPassword, or returns valid User
   ↓
4. Repository Layer: UserRepository.save(user)
   - Converts domain User to ORM UserORM
   - Inserts into database
   ↓
5. Service Layer: Creates verification token
   - Saves to database via VerificationTokenRepository
   ↓
6. Service Layer: Sends email
   - Calls EmailService.send_verification_email()
   ↓
7. API Layer: Formats response as RegisterResponse
   ↓
8. Client: Receives 201 Created with user data
```

## Domain Layer Philosophy

The domain layer is the **heart of the system**. It contains:

- **Entities** (User, Offer, VerificationToken) - Core business objects
- **Value Objects** (Email, Password, Money) - Immutable, validated values
- **Domain Errors** - Specific exceptions for business rule violations
- **Business Logic** - Rules that must always be true (password strength, email format)

**Key principle**: Domain logic has ZERO dependencies on infrastructure. It's pure Python.

This makes it:
- Easy to test (just Python, no database needed)
- Easy to understand (reads like business rules)
- Reusable (can use from CLI, API, batch jobs)

## Service Communication

### Auth Service Responsibilities

```
Registration:
  ✓ Validate email format
  ✓ Validate password strength
  ✓ Check if user already exists
  ✓ Hash password with bcrypt
  ✓ Save user to database
  ✓ Create verification token
  ✓ Send verification email

Login:
  ✓ Find user by email
  ✓ Verify password hash
  ✓ Generate JWT access token (15 min)
  ✓ Generate JWT refresh token (7 days)
  ✓ Return tokens to client

Email Verification:
  ✓ Validate verification token
  ✓ Check token not expired
  ✓ Check token not already used
  ✓ Mark user as verified
  ✓ Mark token as used

Token Refresh:
  ✓ Validate refresh token signature
  ✓ Check token not expired
  ✓ Generate new access token
  ✓ Return new access token
```

### Catalog Service Responsibilities

```
Offer Management:
  ✓ Create offers (partner role)
  ✓ Read offers (all roles)
  ✓ Update offers (partner, own offers only)
  ✓ Delete offers (partner, own offers only)
  ✓ Track quantity and reservations

User Activity (Future):
  ✓ Log offer views
  ✓ Log reservations
  ✓ Log cancellations
  ✓ Support analytics queries

Partner Management:
  ✓ Link partners to places
  ✓ Manage partnerships
```

### Inter-Service Communication

Currently: Services don't call each other (stateless design)

Future: Catalog could call Auth to validate tokens:
```
1. Catalog receives Authorization header
2. Catalog extracts token
3. Catalog calls Auth: GET /auth/validate?token=...
4. Auth validates signature and returns claims
5. Catalog creates CurrentUser from claims
```

## Role-Based Access Control

```
User (Customer)
├─ Browse offers
├─ View offer details
└─ Reserve items

Partner
├─ Create offers (for their place)
├─ Edit own offers
├─ Delete own offers
└─ Browse all offers

Admin
└─ All permissions (future)
```

## Database Design

### Auth Service (est_auth)

**users table**:
- id (UUID, PK)
- email (String, unique, indexed)
- password_hash (String, bcrypt)
- role (String: user, partner, admin)
- is_verified (Boolean)
- created_at, updated_at (DateTime)

**verification_tokens table**:
- token (String, PK)
- user_id (UUID, FK → users.id)
- used (Boolean)
- created_at, expires_at (DateTime)

### Catalog Service (est_catalog)

**offers table**:
- id, place_id, title, description
- price_amount, original_price_amount (Decimal)
- quantity_total, quantity_available (Integer)
- pickup_start, pickup_end (DateTime)
- status (Enum: draft, active, paused, cancelled)
- tags, allergens, image_urls (Arrays)
- created_at, updated_at (DateTime)

**user_history table** (structure only, not yet used):
- id (UUID, PK)
- user_id (UUID, indexed)
- offer_id (UUID, indexed)
- action (Enum: OFFER_VIEWED, OFFERED_RESERVED, etc.)
- details (Text, optional)
- created_at (DateTime, indexed)

**partnerships table**:
- id (UUID, PK)
- partner_user_id (UUID, indexed)
- place_id (UUID, indexed)
- role (String)
- is_active (Boolean)
- created_at, updated_at (DateTime)

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Internet / API Clients          │
└──────────────┬──────────────────────────┘
               │
               ├─── Load Balancer ────┐
               │                      │
     ┌─────────▼─────────┐  ┌────────▼──────────┐
     │  Auth Service     │  │  Catalog Service  │
     │  (8001)           │  │  (8000)           │
     │ Instance 1        │  │ Instance 1        │
     └─────────┬─────────┘  └────────┬──────────┘
               │                      │
               ├───────────┬──────────┤
               │           │          │
        ┌──────▼─┐  ┌──────▼──┐  ┌───▼───────┐
        │ Auth   │  │ Catalog │  │  Shared   │
        │ DB     │  │   DB    │  │ Services  │
        └────────┘  └─────────┘  └───────────┘
```

**Future improvements**:
- Run multiple instances of each service
- Use Redis for caching
- Use message queue for async operations
- Add API Gateway for routing

## Configuration Management

Each service reads from `.env`:

```bash
# Auth Service
- DATABASE_URL
- JWT_SECRET
- JWT_ALGORITHM
- JWT_ACCESS_TOKEN_EXPIRE_MINUTES
- JWT_REFRESH_TOKEN_EXPIRE_DAYS
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

# Catalog Service
- DATABASE_URL
- AUTH_SERVICE_URL
- CATALOG_SERVICE_URL

# Both
- ENV (dev, staging, prod)
```

## Error Handling

**Domain Layer**: Raises specific business exceptions
```python
class InvalidEmail(ValidationError): ...
class WeakPassword(ValidationError): ...
class UserExists(DomainError): ...
class InvalidCredentials(DomainError): ...
```

**Service Layer**: Catches domain exceptions, adds context
```python
try:
    user = service.register(email, password)
except InvalidEmail as e:
    raise ValidationError(f"Email validation failed: {e}")
```

**API Layer**: Catches service exceptions, maps to HTTP status
```python
try:
    ...
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except UserExists as e:
    raise HTTPException(status_code=409, detail=str(e))
```

## Security Considerations

**Password Security**:
- Minimum 8 characters
- Must include uppercase, lowercase, digit
- Hashed with bcrypt (salt included)
- Never logged or stored in plaintext

**Token Security**:
- JWT signed with secret key
- Access tokens: 15 minute expiry (short-lived)
- Refresh tokens: 7 day expiry (longer-lived)
- Tokens must be sent via Authorization header
- No token storage on server (stateless)

**Email Verification**:
- Single-use tokens (marked after use)
- 24-hour expiry
- Prevents fake email registrations

**Authorization**:
- Role-based access control (user, partner, admin)
- Verify ownership (partner can only edit own offers)
- Admin for system-wide operations

---

For step-by-step setup: See [GETTING_STARTED.md](./GETTING_STARTED.md)

For API endpoints: See [API_REFERENCE.md](./API_REFERENCE.md)

For development/testing: See [DEVELOPMENT.md](./DEVELOPMENT.md)
