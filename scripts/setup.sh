#!/bin/bash

# EST Backend - Setup Script
# Automates initial setup: venv, dependencies, databases, migrations

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  EST Backend - Setup Script${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Step 1: Create virtual environment
echo -e "${BLUE}Step 1: Setting up Python virtual environment...${NC}"
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
else
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

source .venv/bin/activate

# Step 2: Install dependencies
echo ""
echo -e "${BLUE}Step 2: Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Setup .env file
echo ""
echo -e "${BLUE}Step 3: Setting up .env file...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file already exists${NC}"
else
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created from template${NC}"
    echo -e "${YELLOW}⚠ Please update .env file with your database URLs${NC}"
fi

# Step 4: Check PostgreSQL
echo ""
echo -e "${BLUE}Step 4: Checking PostgreSQL...${NC}"
if command -v psql &> /dev/null; then
    if psql -U postgres -c "SELECT 1" &>/dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is running${NC}"
    else
        echo -e "${RED}✗ PostgreSQL is not running${NC}"
        echo "Please start PostgreSQL before running migrations"
    fi
else
    echo -e "${YELLOW}⚠ PostgreSQL CLI not found${NC}"
    echo "Make sure PostgreSQL is installed and running"
fi

# Step 5: Create databases
echo ""
echo -e "${BLUE}Step 5: Creating databases...${NC}"
if command -v psql &> /dev/null && psql -U postgres -c "SELECT 1" &>/dev/null; then
    psql -U postgres -c "CREATE DATABASE est_auth;" 2>/dev/null && echo -e "${GREEN}✓ est_auth database created${NC}" || echo -e "${YELLOW}⚠ est_auth database may already exist${NC}"
    psql -U postgres -c "CREATE DATABASE est_catalog;" 2>/dev/null && echo -e "${GREEN}✓ est_catalog database created${NC}" || echo -e "${YELLOW}⚠ est_catalog database may already exist${NC}"
else
    echo -e "${YELLOW}⚠ Skipping database creation (PostgreSQL not available)${NC}"
    echo "Create databases manually:"
    echo "  psql -U postgres -c \"CREATE DATABASE est_auth;\""
    echo "  psql -U postgres -c \"CREATE DATABASE est_catalog;\""
fi

# Step 6: Run migrations
echo ""
echo -e "${BLUE}Step 6: Running database migrations...${NC}"
if command -v psql &> /dev/null && psql -U postgres -c "SELECT 1" &>/dev/null; then
    alembic upgrade head && echo -e "${GREEN}✓ Catalog migrations applied${NC}" || echo -e "${YELLOW}⚠ Catalog migrations failed${NC}"
    alembic -c alembic_auth.ini upgrade head && echo -e "${GREEN}✓ Auth migrations applied${NC}" || echo -e "${YELLOW}⚠ Auth migrations failed${NC}"
else
    echo -e "${YELLOW}⚠ Skipping migrations (PostgreSQL not available)${NC}"
    echo "Run migrations manually after starting PostgreSQL:"
    echo "  alembic upgrade head"
    echo "  alembic -c alembic_auth.ini upgrade head"
fi

# Step 7: Create logs directory
echo ""
echo -e "${BLUE}Step 7: Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Update .env file if needed"
echo "  2. Run: ./run.sh (Linux/macOS) or run.bat (Windows)"
echo "  3. Visit: http://localhost:8001/docs and http://localhost:8000/docs"
echo ""
