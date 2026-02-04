#!/bin/bash

# EST Backend - Run Both Services
# This script starts both Auth and Catalog services in the background

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  EST Backend - Starting Services${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please update .env file with your settings${NC}"
    echo "Starting services anyway (may fail if databases not configured)..."
fi

# Check PostgreSQL connection
echo ""
echo -e "${BLUE}Checking PostgreSQL connection...${NC}"

# Function to check if PostgreSQL is running
check_postgres() {
    if command -v psql &> /dev/null; then
        if psql -U postgres -c "SELECT 1" &>/dev/null; then
            return 0
        fi
    fi
    return 1
}

if ! check_postgres; then
    echo -e "${RED}⚠ PostgreSQL doesn't appear to be running${NC}"
    echo "Make sure PostgreSQL is started before running services"
    echo ""
fi

echo ""
echo -e "${BLUE}Starting Auth Service (Port 8001)...${NC}"

# Start Auth Service in background
uvicorn services.auth.src.main:app --host 0.0.0.0 --port 8001 --reload > logs/auth.log 2>&1 &
AUTH_PID=$!
echo -e "${GREEN}✓ Auth Service started (PID: $AUTH_PID)${NC}"

sleep 2

echo -e "${BLUE}Starting Catalog Service (Port 8000)...${NC}"

# Start Catalog Service in background
uvicorn services.catalog.src.main:app --host 0.0.0.0 --port 8000 --reload > logs/catalog.log 2>&1 &
CATALOG_PID=$!
echo -e "${GREEN}✓ Catalog Service started (PID: $CATALOG_PID)${NC}"

sleep 2

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Both services are running!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Auth Service:"
echo "  - API: http://localhost:8001/docs"
echo "  - Health: http://localhost:8001/health"
echo ""
echo "Catalog Service:"
echo "  - API: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "Logs:"
echo "  - Auth: logs/auth.log"
echo "  - Catalog: logs/catalog.log"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop services${NC}"
echo ""

# Save PIDs to file for cleanup script
mkdir -p .pids
echo $AUTH_PID > .pids/auth.pid
echo $CATALOG_PID > .pids/catalog.pid

# Wait for both services
wait $AUTH_PID $CATALOG_PID
