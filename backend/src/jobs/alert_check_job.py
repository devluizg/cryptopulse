"""
Alert Check Job - Job de verificação de alertas.

Responsável por:
- Verificar condições de alerta
- Gerar alertas quando necessário
- Limpar alertas antigos
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from loguru import logger

from src.jobs.base_job import BaseJob, JobResult
from src.config.jobs_config import JobConfig, ALERT_CHECK_JOB, DATA_CLEANUP_JOB, HEALTH_CHECK_JOB
from src.alerts.alert_manager import alert_manager
from src.database.connection import async_session_maker
from src.database.repositories import AlertRepository


class AlertCheckJob(BaseJob):
    """
    Job de verificação de alertas.
    
    Intervalo: 1 minuto
    
    Verifica scores, preços e outras condições
    para gerar alertas quando necessário.
    """
    
    def __init__(self, config: Optional[JobConfig] = None):
        super().__init__(config or ALERT_CHECK_JOB)
    
    async def execute(self) -> Dict[str, Any]:
        """
        Executa verificação de alertas.
        
        Returns:
            Dict com estatísticas da verificação
        """
        self.logger.info("Iniciando verificação de alertas")
        
        # Executa ciclo de verificação do AlertManager
        result = await alert_manager.run_check_cycle()
        
        stats = {
            "assets_checked": result.get("assets_checked", 0),
            "alerts_created": result.get("alerts_created", 0),
            "alert_ids": result.get("alert_ids", []),
            "duration_seconds": result.get("duration_seconds", 0),
        }
        
        if stats["alerts_created"] > 0:
            self.logger.warning(
                f"⚠️ {stats['alerts_created']} alerta(s) criado(s)"
            )
        else:
            self.logger.debug("Nenhum alerta gerado")
        
        return stats
    
    async def on_success(self, result: JobResult) -> None:
        """Callback após sucesso."""
        alerts_count = result.result_data.get("alerts_created", 0)
        if alerts_count > 0:
            self.logger.info(f"🔔 {alerts_count} novo(s) alerta(s) enviado(s)")


class DataCleanupJob(BaseJob):
    """
    Job de limpeza de dados antigos.
    
    Intervalo: 24 horas (executado às 3h UTC)
    
    Remove:
    - Alertas com mais de 30 dias
    - Scores com mais de 90 dias
    - Transações de whale com mais de 90 dias
    """
    
    # Configurações de retenção (em dias)
    ALERT_RETENTION_DAYS = 30
    SCORE_RETENTION_DAYS = 90
    WHALE_TX_RETENTION_DAYS = 90
    PRICE_RETENTION_DAYS = 365
    
    def __init__(self):
        super().__init__(DATA_CLEANUP_JOB)
    
    async def execute(self) -> Dict[str, Any]:
        """
        Executa limpeza de dados.
        
        Returns:
            Dict com estatísticas da limpeza
        """
        self.logger.info("Iniciando limpeza de dados antigos")
        
        stats = {
            "alerts_deleted": 0,
            "scores_deleted": 0,
            "whale_txs_deleted": 0,
            "prices_deleted": 0,
            "errors": [],
        }
        
        # Limpa alertas
        try:
            deleted = await alert_manager.cleanup_old_alerts(
                days=self.ALERT_RETENTION_DAYS
            )
            stats["alerts_deleted"] = deleted
            self.logger.info(f"Alertas removidos: {deleted}")
        except Exception as e:
            stats["errors"].append(f"Alertas: {str(e)}")
            self.logger.error(f"Erro ao limpar alertas: {e}")
        
        # Limpa scores antigos
        try:
            async with async_session_maker() as session:
                from sqlalchemy import delete
                from src.database.models import AssetScore
                
                cutoff = datetime.utcnow() - timedelta(days=self.SCORE_RETENTION_DAYS)
                
                result = await session.execute(
                    delete(AssetScore).where(AssetScore.calculated_at < cutoff)
                )
                deleted = cast(int, result.rowcount)
                await session.commit()
                
                stats["scores_deleted"] = deleted
                self.logger.info(f"Scores removidos: {deleted}")
        except Exception as e:
            stats["errors"].append(f"Scores: {str(e)}")
            self.logger.error(f"Erro ao limpar scores: {e}")
        
        # Limpa transações de whale antigas
        try:
            async with async_session_maker() as session:
                from sqlalchemy import delete
                from src.database.models import WhaleTransaction
                
                cutoff = datetime.utcnow() - timedelta(days=self.WHALE_TX_RETENTION_DAYS)
                
                result = await session.execute(
                    delete(WhaleTransaction).where(WhaleTransaction.timestamp < cutoff)
                )
                deleted = cast(int, result.rowcount)
                await session.commit()
                
                stats["whale_txs_deleted"] = deleted
                self.logger.info(f"Transações de whale removidas: {deleted}")
        except Exception as e:
            stats["errors"].append(f"Whale TXs: {str(e)}")
            self.logger.error(f"Erro ao limpar whale txs: {e}")
        
        # Limpa preços antigos
        try:
            async with async_session_maker() as session:
                from sqlalchemy import delete
                from src.database.models import PriceData
                
                cutoff = datetime.utcnow() - timedelta(days=self.PRICE_RETENTION_DAYS)
                
                result = await session.execute(
                    delete(PriceData).where(PriceData.timestamp < cutoff)
                )
                deleted = cast(int, result.rowcount)
                await session.commit()
                
                stats["prices_deleted"] = deleted
                self.logger.info(f"Preços removidos: {deleted}")
        except Exception as e:
            stats["errors"].append(f"Prices: {str(e)}")
            self.logger.error(f"Erro ao limpar preços: {e}")
        
        total_deleted = (
            stats["alerts_deleted"] +
            stats["scores_deleted"] +
            stats["whale_txs_deleted"] +
            stats["prices_deleted"]
        )
        
        self.logger.info(f"Limpeza concluída: {total_deleted} registros removidos")
        
        return stats


class HealthCheckJob(BaseJob):
    """
    Job de verificação de saúde.
    
    Intervalo: 2 minutos
    
    Verifica:
    - Conexão com banco de dados
    - Conexão com Redis
    - Status dos coletores
    - Métricas do sistema
    """
    
    def __init__(self):
        super().__init__(HEALTH_CHECK_JOB)
    
    async def execute(self) -> Dict[str, Any]:
        """
        Executa verificação de saúde.
        
        Returns:
            Dict com status dos serviços
        """
        from src.collectors.collector_manager import get_collector_manager
        
        stats = {
            "database": {"status": "unknown"},
            "redis": {"status": "unknown"},
            "collectors": {"status": "unknown"},
            "overall": "unknown",
        }
        
        healthy_count = 0
        total_checks = 3
        
        # Verifica banco de dados
        try:
            async with async_session_maker() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    stats["database"] = {"status": "healthy"}
                    healthy_count += 1
        except Exception as e:
            stats["database"] = {"status": "unhealthy", "error": str(e)}
            self.logger.error(f"Database unhealthy: {e}")
        
        # Verifica Redis
        try:
            import redis.asyncio as redis
            from src.config.settings import settings
            
            r = redis.from_url(settings.redis_url)
            pong = await r.ping()
            if pong:
                stats["redis"] = {"status": "healthy"}
                healthy_count += 1
            await r.close()
        except Exception as e:
            stats["redis"] = {"status": "unhealthy", "error": str(e)}
            self.logger.warning(f"Redis unhealthy: {e}")
        
        # Verifica coletores
        try:
            collector_manager = await get_collector_manager()
            health = await collector_manager.health_check()
            stats["collectors"] = health
            if health.get("status") in ["healthy", "degraded"]:
                healthy_count += 1
        except Exception as e:
            stats["collectors"] = {"status": "unhealthy", "error": str(e)}
            self.logger.error(f"Collectors unhealthy: {e}")
        
        # Status geral
        if healthy_count == total_checks:
            stats["overall"] = "healthy"
        elif healthy_count >= total_checks - 1:
            stats["overall"] = "degraded"
        else:
            stats["overall"] = "unhealthy"
        
        self.logger.info(f"Health check: {stats['overall']} ({healthy_count}/{total_checks})")
        
        return stats
    
    async def on_failure(self, result: JobResult) -> None:
        """Callback em caso de falha - cria alerta de sistema."""
        await alert_manager.create_system_alert(
            component="HealthCheck",
            error_message=result.error or "Health check failed",
        )
