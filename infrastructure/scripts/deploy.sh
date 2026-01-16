#!/bin/bash

# ===========================================
# CryptoPulse - Deploy Script
# ===========================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variáveis
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_DIR="$PROJECT_ROOT/infrastructure/docker"
ENV_FILE="$DOCKER_DIR/.env.production"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           🚀 CryptoPulse - Deploy Script                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar ambiente
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Arquivo .env.production não encontrado!${NC}"
    echo -e "${YELLOW}   Copie .env.production.example para .env.production e configure.${NC}"
    exit 1
fi

# Função de deploy
deploy() {
    echo -e "${BLUE}[1/5] Carregando variáveis de ambiente...${NC}"
    export $(cat "$ENV_FILE" | grep -v '#' | xargs)

    echo -e "${BLUE}[2/5] Construindo imagens...${NC}"
    cd "$DOCKER_DIR"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

    echo -e "${BLUE}[3/5] Parando containers antigos...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

    echo -e "${BLUE}[4/5] Executando migrações...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm backend alembic upgrade head

    echo -e "${BLUE}[5/5] Iniciando novos containers...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    echo -e "${GREEN}✅ Deploy concluído!${NC}"
}

# Função de rollback
rollback() {
    echo -e "${YELLOW}⏪ Executando rollback...${NC}"
    cd "$DOCKER_DIR"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d postgres redis
    
    # Rollback de migração
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm backend alembic downgrade -1
    
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    echo -e "${GREEN}✅ Rollback concluído!${NC}"
}

# Função de status
status() {
    cd "$DOCKER_DIR"
    echo -e "${BLUE}📊 Status dos containers:${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
    
    echo -e "\n${BLUE}📊 Uso de recursos:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Função de logs
logs() {
    cd "$DOCKER_DIR"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f "$@"
}

# Menu
case "$1" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    status)
        status
        ;;
    logs)
        shift
        logs "$@"
        ;;
    *)
        echo "Uso: $0 {deploy|rollback|status|logs [service]}"
        echo ""
        echo "Comandos:"
        echo "  deploy    - Faz deploy da aplicação"
        echo "  rollback  - Reverte para versão anterior"
        echo "  status    - Mostra status dos containers"
        echo "  logs      - Mostra logs (ex: $0 logs backend)"
        exit 1
        ;;
esac
