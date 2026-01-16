"""
CryptoPulse - Main Application
Entrada principal da API FastAPI
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.database.connection import init_db, close_db
from src.utils.logger import setup_logging, logger, get_log_metrics
from src.api.middlewares import LoggingMiddleware


# =========================================
# Configurar Logging (antes de tudo!)
# =========================================
setup_logging(
    level=settings.log_level,
    json_logs=settings.is_production,
    enable_file=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # =========================================
    # STARTUP
    # =========================================
    logger.info("🚀 Iniciando CryptoPulse API...")
    logger.info(f"📋 Ambiente: {settings.environment}")
    logger.info(f"📋 Debug: {settings.debug}")
    logger.info(f"📋 Log Level: {settings.log_level}")
    
    # Inicializa banco (opcional - use migrations em prod)
    # await init_db()
    
    # Inicializa e inicia o scheduler de jobs
    scheduler = None
    if settings.environment != "testing":
        try:
            from src.jobs.scheduler import start_scheduler
            scheduler = await start_scheduler()
            logger.info("✅ Scheduler de jobs iniciado!")
        except Exception as e:
            logger.error(f"⚠️ Erro ao iniciar scheduler: {e}")
    
    logger.info("✅ WebSocket disponível em /ws")
    logger.info("✅ API pronta para receber requisições!")
    
    yield
    
    # =========================================
    # SHUTDOWN
    # =========================================
    logger.info("👋 Encerrando CryptoPulse API...")
    
    # Para o scheduler
    if scheduler:
        try:
            from src.jobs.scheduler import stop_scheduler
            await stop_scheduler()
            logger.info("✅ Scheduler parado!")
        except Exception as e:
            logger.error(f"⚠️ Erro ao parar scheduler: {e}")
    
    # Fecha conexões de banco
    await close_db()
    
    # Fecha collector manager
    try:
        from src.collectors.collector_manager import close_collector_manager
        await close_collector_manager()
        logger.info("✅ Collectors fechados!")
    except Exception as e:
        logger.error(f"⚠️ Erro ao fechar collectors: {e}")
    
    # Log final de métricas
    metrics = get_log_metrics()
    logger.info(
        f"📊 Métricas de log da sessão: "
        f"total={metrics['total']}, errors={metrics['counts']['ERROR']}"
    )
    
    logger.info("✅ CryptoPulse encerrado com sucesso!")


# =========================================
# Criar aplicação
# =========================================
app = FastAPI(
    title=settings.app_name,
    description="API para monitoramento de sinais antecipados no mercado cripto",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# =========================================
# Configurar Middlewares
# =========================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
app.add_middleware(
    LoggingMiddleware,
    exclude_paths=["/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico", "/ws"],
    log_request_body=settings.debug,
    log_response_body=False,
)

# =========================================
# Registrar rotas
# =========================================
from src.api.routes import assets, signals, alerts, health

app.include_router(health.router, tags=["Health"])
app.include_router(assets.router, prefix="/api/v1", tags=["Assets"])
app.include_router(signals.router, prefix="/api/v1", tags=["Signals"])
app.include_router(alerts.router, prefix="/api/v1", tags=["Alerts"])

# Importa e registra rotas de jobs
from src.api.routes import jobs as jobs_router
app.include_router(jobs_router.router, prefix="/api/v1", tags=["Jobs"])

# =========================================
# Registrar WebSocket
# =========================================
from src.api.websocket.router import router as websocket_router
app.include_router(websocket_router, tags=["WebSocket"])


@app.get("/")
async def root():
    """Rota raiz"""
    logger.debug("Rota raiz acessada")
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "websocket": "/ws",
    }
