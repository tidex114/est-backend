# EST Backend

A production-ready microservices backend for EST - a platform connecting restaurants with customers seeking quality food at lower prices.

## 🚀 Quick Start

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Create databases
createdb est_auth && createdb est_catalog

# Run migrations
alembic upgrade head && alembic -c alembic_auth.ini upgrade head

# Start services (in separate terminals)
uvicorn services.auth.src.main:app --port 8001
uvicorn services.catalog.src.main:app --port 8000
```

Visit:
- **Auth API**: http://localhost:8001/docs
- **Catalog API**: http://localhost:8000/docs

## 📚 Documentation

All documentation is in the `/docs` folder:

- **[docs/README.md](./docs/README.md)** - Overview and navigation
- **[docs/GETTING_STARTED.md](./docs/GETTING_STARTED.md)** - Installation and setup
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System design and philosophy
- **[docs/API_REFERENCE.md](./docs/API_REFERENCE.md)** - All endpoints and examples
- **[docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md)** - Testing and debugging
- **[docs/SERVICES.md](./docs/SERVICES.md)** - Service-specific details

## 🏗️ Architecture

**Two main services:**
- **Auth Service** (port 8001) - Registration, login, JWT tokens, email verification
- **Catalog Service** (port 8000) - Offers, reservations, user activity

**Each service uses 7-layer architecture:**
Core → Domain → Models → Repository → Schemas → Services → API

**Key features:**
- ✅ JWT authentication with refresh tokens
- ✅ Email verification with single-use tokens
- ✅ Role-based access control (user, partner, admin)
- ✅ Secure password hashing (bcrypt)
- ✅ Offer CRUD with quantity tracking
- ✅ Per-service PostgreSQL databases
- ✅ Alembic migrations for schema management

## 🛠️ Tech Stack

- FastAPI - Modern async Python web framework
- PostgreSQL - Reliable relational database
- SQLAlchemy - Powerful ORM
- Pydantic - Data validation
- JWT - Stateless authentication
- Bcrypt - Password hashing
- Alembic - Database migrations

## 📄 License

[Add your license]

---

Start with [docs/GETTING_STARTED.md](./docs/GETTING_STARTED.md) to get up and running.
