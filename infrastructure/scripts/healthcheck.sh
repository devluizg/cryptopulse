#!/bin/bash

# ===========================================
# CryptoPulse - Health Check Script
# ===========================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           🏥 CryptoPulse - Health Check                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# Check Backend API
echo -n "Backend API: "
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Unhealthy${NC}"
fi

# Check Frontend
echo -n "Frontend:    "
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Unhealthy${NC}"
fi

# Check PostgreSQL
echo -n "PostgreSQL:  "
if docker exec cryptopulse_postgres pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Unhealthy${NC}"
fi

# Check Redis
echo -n "Redis:       "
if docker exec cryptopulse_redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Unhealthy${NC}"
fi

# Check Nginx
echo -n "Nginx:       "
if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Not running (dev mode)${NC}"
fi

echo ""
echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep cryptopulse || echo "No containers running"
