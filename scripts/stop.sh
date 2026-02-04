#!/bin/bash

# EST Backend - Stop Services
# This script stops both Auth and Catalog services

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}EST Backend - Stopping Services${NC}"
echo ""

# Check if PID files exist
if [ -f ".pids/auth.pid" ]; then
    AUTH_PID=$(cat .pids/auth.pid)
    if kill -0 "$AUTH_PID" 2>/dev/null; then
        echo "Stopping Auth Service (PID: $AUTH_PID)..."
        kill "$AUTH_PID"
        echo -e "${GREEN}✓ Auth Service stopped${NC}"
    fi
    rm .pids/auth.pid
fi

if [ -f ".pids/catalog.pid" ]; then
    CATALOG_PID=$(cat .pids/catalog.pid)
    if kill -0 "$CATALOG_PID" 2>/dev/null; then
        echo "Stopping Catalog Service (PID: $CATALOG_PID)..."
        kill "$CATALOG_PID"
        echo -e "${GREEN}✓ Catalog Service stopped${NC}"
    fi
    rm .pids/catalog.pid
fi

echo ""
echo -e "${GREEN}All services stopped${NC}"
