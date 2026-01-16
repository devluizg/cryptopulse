# ===========================================
# CryptoPulse - Makefile
# ===========================================

.PHONY: help setup up down logs ps check clean

# Variáveis
DOCKER_DIR=infrastructure/docker
BACKEND_DIR=backend

# Cores
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m

help: ## Mostra esta mensagem de ajuda
	@echo ""
	@echo "$(BLUE)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║           🚀 CryptoPulse - Comandos Disponíveis           ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ===========================================
# Docker Commands
# ===========================================

setup: ## Setup inicial completo (primeira vez)
	@./infrastructure/scripts/setup.sh

up: ## Sobe os containers (PostgreSQL + Redis)
	@echo "$(BLUE)🚀 Subindo containers...$(NC)"
	@cd $(DOCKER_DIR) && docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✅ Containers rodando!$(NC)"

down: ## Para os containers
	@echo "$(YELLOW)⏹️  Parando containers...$(NC)"
	@cd $(DOCKER_DIR) && docker-compose down
	@echo "$(GREEN)✅ Containers parados!$(NC)"

restart: ## Reinicia os containers
	@$(MAKE) down
	@$(MAKE) up

logs: ## Mostra logs dos containers
	@cd $(DOCKER_DIR) && docker-compose logs -f

logs-postgres: ## Mostra logs do PostgreSQL
	@docker logs -f cryptopulse_postgres

logs-redis: ## Mostra logs do Redis
	@docker logs -f cryptopulse_redis

ps: ## Lista containers rodando
	@cd $(DOCKER_DIR) && docker-compose ps

# ===========================================
# Backend API Commands
# ===========================================

api: ## Inicia a API FastAPI (modo desenvolvimento)
	@echo "$(BLUE)🚀 Iniciando API...$(NC)"
	@cd $(BACKEND_DIR) && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

api-prod: ## Inicia a API em modo produção
	@echo "$(BLUE)🚀 Iniciando API (produção)...$(NC)"
	@cd $(BACKEND_DIR) && uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# ===========================================
# Jobs Commands
# ===========================================

test-jobs: ## Testa o sistema de jobs
	@echo "$(BLUE)🧪 Testando sistema de jobs...$(NC)"
	@cd $(BACKEND_DIR) && python scripts/test_scheduler.py

run-job: ## Executa um job específico (uso: make run-job JOB=price_collection)
	@echo "$(BLUE)▶️ Executando job: $(JOB)$(NC)"
	@cd $(BACKEND_DIR) && python -c "import asyncio; from src.jobs import get_scheduler, start_scheduler; \
		async def run(): \
			s = await get_scheduler(); \
			await s.initialize(); \
			r = await s.run_job_now('$(JOB)'); \
			print(f'Resultado: {r.success if r else \"Falhou\"}'); \
		asyncio.run(run())"

list-jobs: ## Lista todos os jobs disponíveis
	@echo "$(BLUE)📋 Jobs disponíveis:$(NC)"
	@echo "  - price_collection   (1 min)   - Coleta preços"
	@echo "  - whale_collection   (5 min)   - Coleta transações de whales"
	@echo "  - news_collection    (10 min)  - Coleta notícias"
	@echo "  - oi_collection      (5 min)   - Coleta Open Interest"
	@echo "  - score_calculation  (5 min)   - Calcula Explosion Score"
	@echo "  - alert_check        (1 min)   - Verifica alertas"
	@echo "  - health_check       (2 min)   - Health check do sistema"
	@echo "  - data_cleanup       (diário)  - Limpa dados antigos"

# ===========================================
# Test Commands
# ===========================================

test: ## Executa todos os testes
	@echo "$(BLUE)🧪 Executando testes...$(NC)"
	@cd $(BACKEND_DIR) && pytest tests/ -v

test-repos: ## Testa os repositórios
	@echo "$(BLUE)🧪 Testando repositórios...$(NC)"
	@cd $(BACKEND_DIR) && python scripts/test_repositories.py

test-engine: ## Testa o engine de scores
	@echo "$(BLUE)🧪 Testando engine...$(NC)"
	@cd $(BACKEND_DIR) && python scripts/test_engine.py

test-alerts: ## Testa o sistema de alertas
	@echo "$(BLUE)🧪 Testando alertas...$(NC)"
	@cd $(BACKEND_DIR) && python scripts/test_alerts.py

test-collectors: ## Testa os collectors
	@echo "$(BLUE)🧪 Testando collectors...$(NC)"
	@cd $(BACKEND_DIR) && python scripts/test_collectors.py

test-all: ## Executa todos os scripts de teste
	@echo "$(BLUE)🧪 Executando todos os testes...$(NC)"
	@$(MAKE) test-repos
	@$(MAKE) test-engine
	@$(MAKE) test-alerts
	@$(MAKE) test-jobs
	@echo "$(GREEN)✅ Todos os testes concluídos!$(NC)"

# ===========================================
# Backend Commands
# ===========================================

check: ## Verifica conexões (DB, Redis, APIs)
	@cd $(BACKEND_DIR) && python -m src.utils.check_connections

shell-db: ## Abre shell do PostgreSQL
	@docker exec -it cryptopulse_postgres psql -U cryptopulse -d cryptopulse

shell-redis: ## Abre shell do Redis
	@docker exec -it cryptopulse_redis redis-cli

install: ## Instala dependências do backend
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	@cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

# ===========================================
# Database Commands
# ===========================================

migrate: ## Gera nova migração (uso: make migrate MSG="descricao")
	@cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(MSG)"

migrate-up: ## Aplica todas as migrações pendentes
	@echo "$(BLUE)🔄 Aplicando migrações...$(NC)"
	@cd $(BACKEND_DIR) && alembic upgrade head
	@echo "$(GREEN)✅ Migrações aplicadas!$(NC)"

migrate-down: ## Reverte última migração
	@echo "$(YELLOW)⏪ Revertendo última migração...$(NC)"
	@cd $(BACKEND_DIR) && alembic downgrade -1
	@echo "$(GREEN)✅ Migração revertida!$(NC)"

migrate-history: ## Mostra histórico de migrações
	@cd $(BACKEND_DIR) && alembic history

seed: ## Popula banco com dados iniciais
	@echo "$(BLUE)🌱 Populando banco de dados...$(NC)"
	@cd $(BACKEND_DIR) && python scripts/seed_assets.py
	@echo "$(GREEN)✅ Seed concluído!$(NC)"

db-reset: ## Reset completo do banco (CUIDADO!)
	@echo "$(RED)⚠️  Isso vai APAGAR todos os dados! Tem certeza? [y/N]$(NC)"
	@read -r response; \
	if [ "$$response" = "y" ] || [ "$$response" = "Y" ]; then \
		cd $(BACKEND_DIR) && alembic downgrade base && alembic upgrade head; \
		echo "$(GREEN)✅ Banco resetado!$(NC)"; \
	else \
		echo "Operação cancelada."; \
	fi

# ===========================================
# Cleanup
# ===========================================

clean: ## Remove containers e volumes (CUIDADO: apaga dados!)
	@echo "$(YELLOW)⚠️  Isso vai apagar todos os dados! Tem certeza? [y/N]$(NC)"
	@read -r response; \
	if [ "$$response" = "y" ] || [ "$$response" = "Y" ]; then \
		cd $(DOCKER_DIR) && docker-compose down -v; \
		echo "$(GREEN)✅ Limpeza concluída!$(NC)"; \
	else \
		echo "Operação cancelada."; \
	fi

clean-pycache: ## Remove arquivos __pycache__
	@echo "$(BLUE)🧹 Limpando __pycache__...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cache limpo!$(NC)"

# ===========================================
# Development Workflow
# ===========================================

dev: ## Inicia ambiente de desenvolvimento completo
	@echo "$(BLUE)🚀 Iniciando ambiente de desenvolvimento...$(NC)"
	@$(MAKE) up
	@sleep 3
	@$(MAKE) api

status: ## Mostra status completo do sistema
	@echo ""
	@echo "$(BLUE)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║              📊 Status do Sistema                         ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)🐳 Containers:$(NC)"
	@cd $(DOCKER_DIR) && docker-compose ps
	@echo ""
	@echo "$(YELLOW)🔗 URLs:$(NC)"
	@echo "  API:              http://localhost:8000"
	@echo "  Docs (Swagger):   http://localhost:8000/docs"
	@echo "  Docs (ReDoc):     http://localhost:8000/redoc"
	@echo "  Adminer (DB UI):  http://localhost:8082"
	@echo "  Redis Commander:  http://localhost:8083"
	@echo ""
