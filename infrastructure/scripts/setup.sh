#!/bin/bash

# ===========================================
# CryptoPulse - Setup Script
# ===========================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           🚀 CryptoPulse - Setup Script                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Diretório base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_DIR="$PROJECT_ROOT/infrastructure/docker"

echo -e "${YELLOW}📁 Project root: $PROJECT_ROOT${NC}"

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar Docker
echo -e "\n${BLUE}[1/5] Verificando Docker...${NC}"
if command_exists docker; then
    echo -e "${GREEN}✅ Docker instalado: $(docker --version)${NC}"
else
    echo -e "${RED}❌ Docker não encontrado. Instale em: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Verificar Docker Compose
echo -e "\n${BLUE}[2/5] Verificando Docker Compose...${NC}"
if command_exists docker-compose; then
    echo -e "${GREEN}✅ Docker Compose: $(docker-compose --version)${NC}"
else
    echo -e "${RED}❌ Docker Compose não encontrado${NC}"
    exit 1
fi

# Parar containers existentes do CryptoPulse
echo -e "\n${BLUE}[3/5] Parando containers existentes (se houver)...${NC}"
cd "$DOCKER_DIR"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✅ OK${NC}"

# Subir infraestrutura
echo -e "\n${BLUE}[4/5] Subindo PostgreSQL + Redis...${NC}"
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Aguardar serviços ficarem healthy
echo -e "\n${BLUE}[5/5] Aguardando serviços ficarem prontos...${NC}"

echo -n "⏳ Aguardando PostgreSQL"
for i in {1..30}; do
    if docker exec cryptopulse_postgres pg_isready -U cryptopulse >/dev/null 2>&1; then
        echo -e " ${GREEN}✅${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e " ${RED}❌ Timeout${NC}"
        exit 1
    fi
done

echo -n "⏳ Aguardando Redis"
for i in {1..30}; do
    if docker exec cryptopulse_redis redis-cli ping >/dev/null 2>&1; then
        echo -e " ${GREEN}✅${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e " ${RED}❌ Timeout${NC}"
        exit 1
    fi
done

# Status final
echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           ✅ Setup concluído com sucesso!                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📊 Serviços CryptoPulse:${NC}"
echo -e "   • PostgreSQL:      ${GREEN}localhost:5434${NC}"
echo -e "   • Redis:           ${GREEN}localhost:6380${NC}"
echo -e "   • Adminer (DB UI): ${GREEN}http://localhost:8082${NC}"
echo -e "   • Redis Commander: ${GREEN}http://localhost:8083${NC}"

echo -e "\n${BLUE}🔗 Conexão Adminer:${NC}"
echo -e "   • System:   PostgreSQL"
echo -e "   • Server:   postgres"
echo -e "   • Username: cryptopulse"
echo -e "   • Password: cryptopulse_dev_2024"
echo -e "   • Database: cryptopulse"

echo ""
