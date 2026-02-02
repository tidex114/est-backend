"""
Getting Started - EST Backend

Complete setup and first run guide for local development.

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Git
- pip or poetry

## 1. Installation (5 minutes)

### Clone and Setup Environment

```bash
cd est-backend
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Database Setup (5 minutes)

### Create Databases

```bash
# Connect to PostgreSQL
psql -U postgres

# Create databases
CREATE DATABASE est_auth;
CREATE DATABASE est_catalog;

# Verify
\l
```

### Create Environment File

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
# Auth Service Database
AUTH_DATABASE_URL=postgresql://postgres:password@localhost:5432/est_auth

# Catalog Service Database  
CATALOG_DATABASE_URL=postgresql://postgres:password@localhost:5432/est_catalog

# JWT Configuration (change in production!)
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Email (dev uses mock)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_FROM_EMAIL=noreply@est.local

# Service URLs
AUTH_SERVICE_URL=http://localhost:8001
CATALOG_SERVICE_URL=http://localhost:8000

# Environment
ENV=dev
```

## 3. Run Migrations (3 minutes)

### Apply Database Schema

```bash
# Catalog migrations
alembic upgrade head

# Auth migrations
alembic -c alembic_auth.ini upgrade head
```

Verify:
```bash
psql -U postgres -d est_auth -c "\dt"
psql -U postgres -d est_catalog -c "\dt"
```

## 4. Start Services (2 minutes)

### Terminal 1: Auth Service

```bash
python -m uvicorn services.auth.src.main:app --host 0.0.0.0 --port 8001 --reload
```

Visit: http://localhost:8001/health → Should see `{"status": "ok"}`

### Terminal 2: Catalog Service

```bash
python -m uvicorn services.catalog.src.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit: http://localhost:8000/health → Should see `{"status": "ok"}`

## 5. Test It Works (3 minutes)

### Register a User

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "role": "user"
  }'
```

Response:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "role": "user",
    "is_verified": false
  },
  "message": "Registration successful. Check your email for verification link."
}
```

### Get Verification Token

In dev mode, the verification link is printed to the auth service terminal:

```
[MOCK EMAIL]
To: test@example.com
Verification Token: xxx_token_xxx
...
```

### Verify Email

```bash
curl -X POST http://localhost:8001/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "xxx_token_xxx"}'
```

### Login

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

Response includes `access_token` and `refresh_token`.

### List Offers (Test Catalog)

```bash
curl -X GET http://localhost:8000/offers \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

✅ **You're done! Services are running.**

## Interactive API Documentation

Both services provide Swagger UI:

- **Auth Service**: http://localhost:8001/docs
- **Catalog Service**: http://localhost:8000/docs

Click "Try it out" on any endpoint to test interactively.

## Common Issues & Solutions

### "No such module 'services'"

**Solution**: Run from project root:
```bash
cd est-backend
python -m uvicorn services.auth.src.main:app --port 8001
```

### "Database connection refused"

**Solution**: Start PostgreSQL:
```bash
# macOS
brew services start postgresql

# Ubuntu/Debian
sudo systemctl start postgresql

# Windows
# Use Services app or pgAdmin
```

### "Alembic: No 'script_location' key found"

**Solution**: Use correct config file:
```bash
# For auth service
alembic -c alembic_auth.ini upgrade head
```

### "Email verification not working"

**Solution**: Check terminal output. In dev mode, tokens are printed:
```
[MOCK EMAIL]
To: test@example.com
Verification Token: ...
```

### "Invalid token" errors

**Solution**: Make sure:
1. Token is from successful login (not registration)
2. Format is `Authorization: Bearer <token>`
3. Token hasn't expired (access tokens last 15 minutes)

## Reset Everything (⚠️ Deletes All Data)

```bash
# Drop and recreate databases
psql -U postgres -c "DROP DATABASE est_auth; CREATE DATABASE est_auth;"
psql -U postgres -c "DROP DATABASE est_catalog; CREATE DATABASE est_catalog;"

# Re-run migrations
alembic upgrade head
alembic -c alembic_auth.ini upgrade head
```

## Next Steps

1. **Understand Architecture**: Read [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Try All Endpoints**: See [API_REFERENCE.md](./API_REFERENCE.md)
3. **Test Everything**: Follow [DEVELOPMENT.md](./DEVELOPMENT.md)
4. **Learn Services**: Check [SERVICES.md](./SERVICES.md)

## Environment Variables Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `AUTH_DATABASE_URL` | (required) | Auth service database |
| `CATALOG_DATABASE_URL` | (required) | Catalog service database |
| `JWT_SECRET` | (required in prod) | Secret for JWT signing |
| `JWT_ALGORITHM` | HS256 | JWT algorithm |
| `SMTP_HOST` | localhost | Email server |
| `SMTP_PORT` | 1025 | Email server port |
| `AUTH_SERVICE_URL` | http://localhost:8001 | Auth service URL |
| `CATALOG_SERVICE_URL` | http://localhost:8000 | Catalog service URL |
| `ENV` | dev | Environment |

---

**Status**: ✅ Setup complete!

Next: Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system.
