"""
Score Calculation Job - Job de cálculo de scores.

Responsável por:
- Calcular Explosion Score para todos os ativos
- Persistir scores no banco
- Identificar mudanças significativas
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger

from src.jobs.base_job import BaseJob, JobResult
from src.config.jobs_config import JobConfig, SCORE_CALCULATION_JOB
from src.engine.engine_manager import EngineManager
from src.collectors.collector_manager import get_collector_manager
from src.database.connection import async_session_maker
from src.database.repositories import AssetRepository, ScoreRepository


class ScoreCalculationJob(BaseJob):
    """
    Job de cálculo de scores.
    
    Intervalo: 5 minutos
    
    Calcula o Explosion Score para todos os ativos ativos
    usando dados coletados.
    """
    
    def __init__(self, config: Optional[JobConfig] = None):
        super().__init__(config or SCORE_CALCULATION_JOB)
        self._engine_manager: Optional[EngineManager] = None
    
    async def setup(self) -> None:
        """Inicializa o engine manager."""
        if not self._engine_manager:
            self._engine_manager = EngineManager()
            collector_manager = await get_collector_manager()
            await self._engine_manager.initialize(collector_manager)
    
    async def cleanup(self) -> None:
        """Limpa recursos."""
        # Não fecha o engine manager aqui pois é reutilizado
        pass
    
    async def execute(self) -> Dict[str, Any]:
        """
        Executa cálculo de scores para todos os ativos.
        
        Returns:
            Dict com estatísticas do cálculo
        """
        if not self._engine_manager:
            raise RuntimeError("EngineManager não inicializado")
        
        self.logger.info("Iniciando ciclo de cálculo de scores")
        
        # Executa o ciclo de cálculo
        result = await self._engine_manager.run_calculation_cycle()
        
        # Formata estatísticas
        stats = {
            "assets_processed": result.get("assets_processed", 0),
            "scores_created": result.get("scores_created", 0),
            "duration_seconds": result.get("duration_seconds", 0),
            "errors": result.get("errors", []),
            "scores_summary": {},
        }
        
        # Cria resumo dos scores por status
        scores = result.get("scores", {})
        status_count = {"high": 0, "attention": 0, "low": 0}
        high_assets = []
        
        for symbol, score_data in scores.items():
            status = score_data.get("status", "low").lower()
            status_count[status] = status_count.get(status, 0) + 1
            
            if status == "high":
                high_assets.append({
                    "symbol": symbol,
                    "score": score_data.get("score", 0),
                })
        
        stats["scores_summary"] = {
            "by_status": status_count,
            "high_assets": sorted(high_assets, key=lambda x: x["score"], reverse=True),
        }
        
        self.logger.info(
            f"Scores calculados: {stats['scores_created']}, "
            f"HIGH: {status_count['high']}, "
            f"ATTENTION: {status_count['attention']}, "
            f"LOW: {status_count['low']}"
        )
        
        return stats
    
    async def on_success(self, result: JobResult) -> None:
        """
        Callback após sucesso.
        Loga ativos em zona de explosão.
        """
        summary = result.result_data.get("scores_summary", {})
        high_assets = summary.get("high_assets", [])
        
        if high_assets:
            self.logger.warning(
                f"⚠️ {len(high_assets)} ativo(s) em zona de EXPLOSÃO: "
                f"{', '.join(a['symbol'] for a in high_assets[:5])}"
            )


class SingleAssetScoreJob(BaseJob):
    """
    Job de cálculo de score para um único ativo.
    
    Útil para recálculo sob demanda.
    """
    
    def __init__(self, symbol: str):
        config = JobConfig(
            job_id=f"score_calculation_{symbol.lower()}",
            name=f"Cálculo de Score - {symbol}",
            description=f"Calcula score para {symbol}",
            interval_seconds=0,  # Não é agendado
            timeout_seconds=60,
            max_retries=2,
            tags=["engine", "scores", "single"],
        )
        super().__init__(config)
        self.symbol = symbol.upper()
        self._engine_manager: Optional[EngineManager] = None
    
    async def setup(self) -> None:
        """Inicializa o engine manager."""
        if not self._engine_manager:
            self._engine_manager = EngineManager()
            collector_manager = await get_collector_manager()
            await self._engine_manager.initialize(collector_manager)
    
    async def execute(self) -> Dict[str, Any]:
        """
        Calcula score para o ativo específico.
        
        Returns:
            Dict com resultado do cálculo
        """
        if not self._engine_manager:
            raise RuntimeError("EngineManager não inicializado")
        
        self.logger.info(f"Calculando score para {self.symbol}")
        
        result = await self._engine_manager.calculate_single_asset(self.symbol)
        
        stats = {
            "symbol": self.symbol,
            "explosion_score": result.get("explosion_score", 0),
            "status": result.get("status", "unknown"),
            "indicator_scores": result.get("indicator_scores", {}),
            "score_id": result.get("score_id"),
        }
        
        self.logger.info(
            f"{self.symbol}: score={stats['explosion_score']:.1f}, "
            f"status={stats['status']}"
        )
        
        return stats
