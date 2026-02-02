"""
Development Guide - EST Backend

Testing, debugging, and development workflows.

## Testing Overview

You can test the EST backend using multiple tools:

- **Swagger UI** (Browser) - Interactive, visual, easiest
- **cURL** (Command Line) - Simple, quick tests
- **Postman** (App) - Professional API testing with collections

## Interactive Testing (Recommended)

Both services provide Swagger UI documentation:

- **Auth Service**: http://localhost:8001/docs
- **Catalog Service**: http://localhost:8000/docs

### How to Use Swagger UI

1. Go to http://localhost:8001/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. View response

This is the easiest way to test all endpoints without command line.

## Testing Workflows

### Workflow 1: User Registration and Login

**Goal**: Register a user, verify email, login, and get token

```bash
# 1. Register User
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "role": "user"
  }'

# Expected: 201 Created with user data and message
# Check auth service terminal for verification token

# 2. Verify Email
curl -X POST http://localhost:8001/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN_FROM_TERMINAL"}'

# Expected: 200 OK, user.is_verified = true

# 3. Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'

# Expected: 200 OK with access_token and refresh_token
# Save these tokens for next steps

# 4. Test Access Token
curl -X GET http://localhost:8000/offers \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Expected: 200 OK with empty offers list
```

### Workflow 2: Partner Creates and Manages Offers

```bash
# 1. Register Partner (role: "partner")
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "partner@example.com",
    "password": "PartnerPass123",
    "role": "partner"
  }'

# 2. Verify Partner Email
# Get token from terminal, then verify

# 3. Partner Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "partner@example.com",
    "password": "PartnerPass123"
  }'

# Save partner_token and partner_id

# 4. Create Offer
curl -X POST http://localhost:8000/offers \
  -H "Authorization: Bearer PARTNER_TOKEN" \
  -H "X-User-ID: PARTNER_ID" \
  -H "X-User-Email: partner@example.com" \
  -H "X-User-Role: partner" \
  -H "X-Place-ID: 550e8400-e29b-41d4-a716-446655440001" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fresh Pizza",
    "description": "Delicious homemade pizza",
    "price_amount": 299.99,
    "price_currency": "RUB",
    "original_price_amount": 499.99,
    "original_price_currency": "RUB",
    "quantity_total": 10,
    "pickup_start": "2024-12-01T15:00:00Z",
    "pickup_end": "2024-12-01T19:00:00Z",
    "tags": ["pizza"],
    "allergens": ["gluten"],
    "image_urls": []
  }'

# Expected: 201 Created with offer_id

# 5. Update Offer
curl -X PATCH http://localhost:8000/offers/OFFER_ID \
  -H "Authorization: Bearer PARTNER_TOKEN" \
  -H "X-User-ID: PARTNER_ID" \
  -H "X-User-Email: partner@example.com" \
  -H "X-User-Role: partner" \
  -H "X-Place-ID: 550e8400-e29b-41d4-a716-446655440001" \
  -H "Content-Type: application/json" \
  -d '{"title": "Fresh Homemade Pizza"}'

# Expected: 200 OK with updated offer

# 6. Delete Offer
curl -X DELETE http://localhost:8000/offers/OFFER_ID \
  -H "Authorization: Bearer PARTNER_TOKEN" \
  -H "X-User-ID: PARTNER_ID" \
  -H "X-User-Email: partner@example.com" \
  -H "X-User-Role: partner" \
  -H "X-Place-ID: 550e8400-e29b-41d4-a716-446655440001"

# Expected: 204 No Content
```

### Workflow 3: Customer Reserves Offer

```bash
# Prerequisites: Partner has created an offer

# 1. Register and Login as Customer
# (Same as Workflow 1)

# 2. List Offers
curl -X GET http://localhost:8000/offers \
  -H "Authorization: Bearer CUSTOMER_TOKEN"

# Expected: 200 OK with list of offers

# 3. Get Offer Details
curl -X GET http://localhost:8000/offers/OFFER_ID \
  -H "Authorization: Bearer CUSTOMER_TOKEN"

# Expected: 200 OK with offer details

# 4. Reserve Offer
curl -X POST http://localhost:8000/offers/OFFER_ID/reserve \
  -H "Authorization: Bearer CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 2}'

# Expected: 200 OK with reservation confirmation
```

### Workflow 4: Token Refresh

```bash
# When access token expires (after 15 minutes):

curl -X POST http://localhost:8001/auth/refresh-token \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'

# Expected: 200 OK with new access_token
```

## Error Testing

### Invalid Email

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "password": "ValidPass123"
  }'

# Expected: 400 Bad Request - "Invalid email format"
```

### Weak Password

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "weak"
  }'

# Expected: 400 Bad Request - "Password must be at least 8 characters"
```

### Duplicate Email

```bash
# Register twice with same email
# First: 201 Created
# Second: 409 Conflict - "User already exists"
```

### Invalid Credentials

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "AnyPassword123"
  }'

# Expected: 401 Unauthorized - "Invalid email or password"
```

### Unauthorized Access (Missing Token)

```bash
curl -X GET http://localhost:8000/offers

# Expected: 401 Unauthorized - Missing Authorization header
```

### Forbidden (Insufficient Permissions)

```bash
# Try to create offer as customer (user role)
curl -X POST http://localhost:8000/offers \
  -H "Authorization: Bearer CUSTOMER_TOKEN" \
  -H "X-User-Role: user" \
  ...

# Expected: 403 Forbidden - "Partner role required"
```

### Not Found

```bash
curl -X GET http://localhost:8000/offers/invalid-uuid \
  -H "Authorization: Bearer TOKEN"

# Expected: 404 Not Found - "Offer not found"
```

## Database Inspection

### View Users

```bash
psql -U postgres -d est_auth -c "SELECT id, email, role, is_verified FROM users;"
```

### View Offers

```bash
psql -U postgres -d est_catalog -c "SELECT id, title, price_amount, quantity_available FROM offers;"
```

### View Verification Tokens

```bash
psql -U postgres -d est_auth -c "SELECT token, user_id, used, expires_at FROM verification_tokens LIMIT 5;"
```

## Debugging Tips

### Check Service Logs

Look at terminal where services are running:
- Auth service: http://localhost:8001
- Catalog service: http://localhost:8000

### View Mock Emails

In dev mode, verification emails are printed to the auth service terminal:

```
[MOCK EMAIL]
To: user@example.com
Subject: Verify your EST account
Verification Token: xyz_token_xyz
...
```

### Test Database Connection

```bash
# Auth database
psql -U postgres -d est_auth -c "SELECT 1"

# Catalog database
psql -U postgres -d est_catalog -c "SELECT 1"
```

### Check Running Services

```bash
# Should see both services listening
lsof -i :8000
lsof -i :8001
```

## Performance Testing

### Single Request Timing

```bash
time curl http://localhost:8000/offers \
  -H "Authorization: Bearer TOKEN"
```

### Concurrent Requests

```bash
for i in {1..10}; do
  curl http://localhost:8000/offers \
    -H "Authorization: Bearer TOKEN" &
done
wait
```

## Tips for Testing

1. **Save Tokens in Variables**: Makes testing easier without retyping
   ```bash
   TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   curl -H "Authorization: Bearer $TOKEN" ...
   ```

2. **Use Timestamps for Unique Emails**:
   ```bash
   EMAIL="test_$(date +%s)@example.com"
   ```

3. **Keep Terminal Output Visible**: Important for dev mode (verification tokens are printed)

4. **Test Both Success and Error Cases**: Don't just test happy path

5. **Check Swagger UI First**: It's easier and more visual than cURL

## Common Issues

### "Missing Authorization header"
→ Make sure you include: `Authorization: Bearer <token>`

### "Invalid or expired token"
→ Token may have expired (access tokens last 15 minutes) or be invalid. Re-login to get new token.

### "Partner role required"
→ You're using a customer (user) token. Use a partner token or change X-User-Role header.

### "Offer not found"
→ Check offer ID is correct. List all offers first to get valid ID.

### Email not being sent
→ In dev mode, emails are printed to terminal. Check auth service terminal output.

---

For API details, see [API_REFERENCE.md](./API_REFERENCE.md)

For architecture details, see [ARCHITECTURE.md](./ARCHITECTURE.md)
