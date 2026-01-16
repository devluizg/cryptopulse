"""
CryptoPulse - Health Check Routes
Endpoints para verificar saúde da aplicação
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from src.config.settings import settings
from src.database.connection import get_session
from src.utils.logger import get_log_metrics, logger_config

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/health/detailed")
async def detailed_health_check(
    session: AsyncSession = Depends(get_session)
):
    """Health check detalhado com status dos serviços"""
    
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {}
    }
    
    # Verificar PostgreSQL
    try:
        await session.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "type": "postgresql"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Verificar Redis
    try:
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.aclose()
        health_status["checks"]["cache"] = {
            "status": "healthy",
            "type": "redis"
        }
    except Exception as e:
        health_status["checks"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Verificar Logs
    log_metrics = get_log_metrics()
    log_dir = logger_config.get_log_dir()
    
    log_status = {
        "status": "healthy",
        "configured": logger_config.is_configured,
        "log_directory": str(log_dir) if log_dir else None,
        "metrics": {
            "total_logs": log_metrics["total"],
            "errors_last_hour": log_metrics["errors_last_hour"],
        }
    }
    
    # Verificar se diretório de logs existe
    if log_dir and log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        log_status["log_files_count"] = len(log_files)
    
    # Alertar se muitos erros
    if log_metrics["errors_last_hour"] > 100:
        log_status["status"] = "warning"
        log_status["warning"] = "High error rate in last hour"
    
    health_status["checks"]["logging"] = log_status
    
    return health_status


@router.get("/health/logs")
async def logs_health():
    """
    Endpoint específico para métricas de logs.
    """
    metrics = get_log_metrics()
    log_dir = logger_config.get_log_dir()
    
    response = {
        "metrics": metrics,
        "config": {
            "configured": logger_config.is_configured,
            "log_directory": str(log_dir) if log_dir else None,
            "log_level": settings.log_level,
        },
        "files": []
    }
    
    # Listar arquivos de log
    if log_dir and log_dir.exists():
        for log_file in sorted(log_dir.glob("*.log*")):
            stat = log_file.stat()
            response["files"].append({
                "name": log_file.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
            })
    
    return response
