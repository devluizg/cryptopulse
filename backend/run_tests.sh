#!/bin/bash

echo "==================================="
echo "CryptoPulse - Test Runner"
echo "==================================="

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Ativar venv se não estiver ativo
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
fi

# Instalar dependências de teste se necessário
pip install -q aiosqlite httpx

echo ""
echo "Running unit tests..."
echo "-----------------------------------"
pytest tests/unit/ -v --tb=short 2>&1

UNIT_EXIT=$?

echo ""
echo "Running integration tests..."
echo "-----------------------------------"
pytest tests/integration/ -v --tb=short 2>&1

INTEGRATION_EXIT=$?

echo ""
echo "==================================="
echo "Test Summary"
echo "==================================="

if [ $UNIT_EXIT -eq 0 ]; then
    echo -e "Unit Tests: ${GREEN}PASSED${NC}"
else
    echo -e "Unit Tests: ${RED}FAILED${NC}"
fi

if [ $INTEGRATION_EXIT -eq 0 ]; then
    echo -e "Integration Tests: ${GREEN}PASSED${NC}"
else
    echo -e "Integration Tests: ${RED}FAILED${NC}"
fi

echo ""
echo "Coverage report:"
echo "-----------------------------------"
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html 2>&1 | tail -20

echo ""
echo "HTML coverage report generated in: htmlcov/index.html"
