#!/bin/bash

# ===========================================
# CryptoPulse - Backup Script
# ===========================================

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configurações
BACKUP_DIR="/opt/cryptopulse/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}🗄️  Iniciando backup - $DATE${NC}"

# Backup do PostgreSQL
echo -e "${BLUE}[1/3] Backup do PostgreSQL...${NC}"
docker exec cryptopulse_postgres pg_dump -U cryptopulse cryptopulse | gzip > "$BACKUP_DIR/postgres_$DATE.sql.gz"

# Backup do Redis
echo -e "${BLUE}[2/3] Backup do Redis...${NC}"
docker exec cryptopulse_redis redis-cli BGSAVE
sleep 2
docker cp cryptopulse_redis:/data/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"

# Limpar backups antigos
echo -e "${BLUE}[3/3] Limpando backups antigos...${NC}"
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete

echo -e "${GREEN}✅ Backup concluído!${NC}"
echo -e "   📁 Local: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"
