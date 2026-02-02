# API Reference - EST Backend

Complete reference for all endpoints, request/response formats, and error codes.

## Quick Reference

**Auth Service** (Port 8001)
- POST /auth/register - Create user account
- POST /auth/login - Authenticate
- POST /auth/verify-email - Confirm email
- POST /auth/refresh-token - Get new access token

**Catalog Service** (Port 8000)
- GET /offers - List offers
- GET /offers/{id} - Get offer details
- POST /offers - Create offer (partner)
- PATCH /offers/{id} - Update offer (partner)
- DELETE /offers/{id} - Delete offer (partner)
- POST /offers/{id}/reserve - Reserve items (user)

## Auth Service (Port 8001)

### Register User

```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "role": "user"
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "user",
    "is_verified": false
  },
  "message": "Registration successful. Check your email for verification link."
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

### Login

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response** (200 OK):
```json
{
  "user": {...},
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

### Verify Email

```bash
POST /auth/verify-email
Content-Type: application/json

{
  "token": "verification_token_from_email"
}
```

**Response** (200 OK): Updated user with `is_verified: true`

### Refresh Token

```bash
POST /auth/refresh-token
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

**Response** (200 OK): New access and refresh tokens

## Catalog Service (Port 8000)

### List Offers (Customer)

```bash
GET /offers
Authorization: Bearer <access_token>
```

**Response** (200 OK): Array of offer objects

### Get Offer Details

```bash
GET /offers/{offer_id}
Authorization: Bearer <access_token>
```

**Response** (200 OK): Single offer object

### Create Offer (Partner)

```bash
POST /offers
Authorization: Bearer <token>
X-User-ID: <user_id>
X-User-Email: <email>
X-User-Role: partner
X-Place-ID: <place_id>
Content-Type: application/json

{
  "title": "Fresh Pizza",
  "description": "Delicious pizza",
  "price_amount": 299.99,
  "price_currency": "RUB",
  "original_price_amount": 499.99,
  "original_price_currency": "RUB",
  "quantity_total": 10,
  "pickup_start": "2024-01-01T15:00:00Z",
  "pickup_end": "2024-01-01T19:00:00Z",
  "tags": ["pizza"],
  "allergens": ["gluten"],
  "image_urls": []
}
```

**Response** (201 Created): Created offer

### Update Offer (Partner)

```bash
PATCH /offers/{offer_id}
Authorization: Bearer <token>
X-User-ID: <user_id>
X-User-Email: <email>
X-User-Role: partner
X-Place-ID: <place_id>
Content-Type: application/json

{
  "title": "Updated Title",
  "quantity_available": 5
}
```

**Response** (200 OK): Updated offer

### Delete Offer (Partner)

```bash
DELETE /offers/{offer_id}
Authorization: Bearer <token>
X-User-ID: <user_id>
X-User-Email: <email>
X-User-Role: partner
X-Place-ID: <place_id>
```

**Response** (204 No Content)

### Reserve Offer (Customer)

```bash
POST /offers/{offer_id}/reserve
Authorization: Bearer <token>
Content-Type: application/json

{
  "quantity": 2
}
```

**Response** (200 OK):
```json
{
  "offer_id": "offer-id-1",
  "quantity_reserved": 2,
  "message": "Successfully reserved 2 item(s)."
}
```

## Token Usage

Include in all authenticated requests:
```bash
Authorization: Bearer <access_token>
```

**Access Token**: 15 minutes expiry
**Refresh Token**: 7 days expiry

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate, insufficient quantity) |

## Role Permissions

| Action | User | Partner | Admin |
|--------|------|---------|-------|
| Browse offers | ✅ | ✅ | ✅ |
| Create offers | ❌ | ✅ | ✅ |
| Edit own offers | ❌ | ✅ | ✅ |
| Delete own offers | ❌ | ✅ | ✅ |
| Edit all offers | ❌ | ❌ | ✅ |

## Health Checks

```bash
# Auth service health
GET http://localhost:8001/health

# Catalog service health
GET http://localhost:8000/health
```

---

See [DEVELOPMENT.md](./DEVELOPMENT.md) for testing examples.
