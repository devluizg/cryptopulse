"""
CryptoPulse Scheduler - Orquestrador de Jobs.

Responsável por:
- Gerenciar ciclo de vida dos jobs
- Agendar execuções
- Monitorar status
- Fornecer API para controle
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
import asyncio
from enum import Enum

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    JobExecutionEvent,
)
from loguru import logger

from src.config.jobs_config import (
    SCHEDULER_CONFIG,
    ALL_JOBS,
    JobConfig,
)
from src.jobs.base_job import BaseJob, JobResult


class SchedulerState(str, Enum):
    """Estados do scheduler."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"


class CryptoPulseScheduler:
    """
    Scheduler central do CryptoPulse.
    
    Gerencia todos os jobs agendados do sistema:
    - Coleta de dados (preços, whales, news, OI)
    - Cálculo de scores
    - Verificação de alertas
    - Manutenção (cleanup)
    - Health checks
    """
    
    def __init__(self):
        """Inicializa o scheduler."""
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._state = SchedulerState.STOPPED
        self._jobs: Dict[str, BaseJob] = {}
        self._job_configs: Dict[str, JobConfig] = {}
        self._start_time: Optional[datetime] = None
        
        # Estatísticas globais
        self._total_executions = 0
        self._total_errors = 0
        self._last_execution: Optional[datetime] = None
        
        self.logger = logger.bind(component="scheduler")
    
    async def initialize(self) -> None:
        """
        Inicializa o scheduler e registra jobs.
        
        Deve ser chamado antes de start().
        """
        if self._state != SchedulerState.STOPPED:
            self.logger.warning("Scheduler já inicializado")
            return
        
        self._state = SchedulerState.STARTING
        self.logger.info("Inicializando CryptoPulse Scheduler...")
        
        # Cria scheduler APScheduler
        self._scheduler = AsyncIOScheduler(
            timezone=SCHEDULER_CONFIG.timezone,
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 60,
            },
        )
        
        # Registra listeners de eventos
        self._scheduler.add_listener(
            self._on_job_executed,
            EVENT_JOB_EXECUTED,
        )
        self._scheduler.add_listener(
            self._on_job_error,
            EVENT_JOB_ERROR,
        )
        self._scheduler.add_listener(
            self._on_job_missed,
            EVENT_JOB_MISSED,
        )
        
        # Registra jobs
        await self._register_jobs()
        
        self.logger.info(f"Scheduler inicializado com {len(self._jobs)} jobs")
    
    async def _register_jobs(self) -> None:
        """Registra todos os jobs configurados."""
        from src.jobs.data_collection_job import (
            PriceCollectionJob,
            WhaleCollectionJob,
            NewsCollectionJob,
            OpenInterestCollectionJob,
        )
        from src.jobs.score_calculation_job import ScoreCalculationJob
        from src.jobs.alert_check_job import (
            AlertCheckJob,
            DataCleanupJob,
            HealthCheckJob,
        )
        
        for job_id in SCHEDULER_CONFIG.enabled_jobs:
            job_config = ALL_JOBS.get(job_id)
            
            if not job_config or not job_config.enabled:
                continue
            
            job_instance: Optional[BaseJob] = None
            
            # Cria instância baseado no job_id
            if job_id == "price_collection":
                job_instance = PriceCollectionJob(job_config)
            elif job_id == "whale_collection":
                job_instance = WhaleCollectionJob(job_config)
            elif job_id == "news_collection":
                job_instance = NewsCollectionJob(job_config)
            elif job_id == "oi_collection":
                job_instance = OpenInterestCollectionJob(job_config)
            elif job_id == "score_calculation":
                job_instance = ScoreCalculationJob(job_config)
            elif job_id == "alert_check":
                job_instance = AlertCheckJob(job_config)
            elif job_id == "data_cleanup":
                job_instance = DataCleanupJob()
            elif job_id == "health_check":
                job_instance = HealthCheckJob()
            
            if job_instance:
                self._jobs[job_id] = job_instance
                self._job_configs[job_id] = job_config
                
                self.logger.debug(
                    f"Job registrado: {job_id} "
                    f"(intervalo: {job_config.interval_seconds}s)"
                )
        
        # Registra cleanup como cron job (3h UTC diariamente) se não estiver
        if "data_cleanup" not in self._jobs:
            cleanup_config = ALL_JOBS.get("data_cleanup")
            if cleanup_config:
                cleanup_job = DataCleanupJob()
                self._jobs["data_cleanup"] = cleanup_job
                self._job_configs["data_cleanup"] = cleanup_config
    
    async def start(self) -> None:
        """
        Inicia o scheduler.
        
        Agenda todos os jobs e começa a execução.
        """
        if self._state == SchedulerState.RUNNING:
            self.logger.warning("Scheduler já está rodando")
            return
        
        if self._state == SchedulerState.STOPPED:
            await self.initialize()
        
        if not self._scheduler:
            raise RuntimeError("Scheduler não inicializado")
        
        self.logger.info("Iniciando scheduler...")
        
        # Agenda jobs com intervalo
        for job_id, job in self._jobs.items():
            config = self._job_configs[job_id]
            
            if job_id == "data_cleanup":
                # Cleanup usa cron (3h UTC)
                trigger = CronTrigger(hour=3, minute=0, timezone="UTC")
            else:
                # Outros usam intervalo
                trigger = IntervalTrigger(
                    seconds=config.interval_seconds,
                    timezone=SCHEDULER_CONFIG.timezone,
                )
            
            # Adiciona job ao scheduler
            self._scheduler.add_job(
                self._run_job,
                trigger=trigger,
                args=[job_id],
                id=job_id,
                name=config.name,
                replace_existing=True,
            )
            
            self.logger.debug(f"Job agendado: {job_id}")
        
        # Inicia o scheduler
        self._scheduler.start()
        self._state = SchedulerState.RUNNING
        self._start_time = datetime.utcnow()
        
        self.logger.info("✅ Scheduler iniciado!")
        
        # Executa jobs iniciais após delay
        if SCHEDULER_CONFIG.startup_delay_seconds > 0:
            self.logger.info(
                f"Aguardando {SCHEDULER_CONFIG.startup_delay_seconds}s "
                "antes da primeira execução..."
            )
            asyncio.create_task(self._run_initial_jobs())
    
    async def _run_initial_jobs(self) -> None:
        """Executa jobs iniciais com stagger."""
        await asyncio.sleep(SCHEDULER_CONFIG.startup_delay_seconds)
        
        # Ordem de execução inicial
        initial_order = [
            "health_check",
            "price_collection",
            "whale_collection",
            "oi_collection",
            "news_collection",
            "score_calculation",
            "alert_check",
        ]
        
        for job_id in initial_order:
            if job_id in self._jobs and self._state == SchedulerState.RUNNING:
                self.logger.info(f"Execução inicial: {job_id}")
                await self._run_job(job_id)
                await asyncio.sleep(SCHEDULER_CONFIG.job_stagger_seconds)
    
    async def stop(self) -> None:
        """
        Para o scheduler.
        
        Aguarda jobs em execução terminarem.
        """
        if self._state != SchedulerState.RUNNING:
            self.logger.warning("Scheduler não está rodando")
            return
        
        self._state = SchedulerState.STOPPING
        self.logger.info("Parando scheduler...")
        
        # Para o APScheduler
        if self._scheduler:
            self._scheduler.shutdown(wait=True)
        
        # Para jobs em execução
        for job_id, job in self._jobs.items():
            if job.is_running:
                self.logger.info(f"Parando job: {job_id}")
                job.stop()
        
        self._state = SchedulerState.STOPPED
        self.logger.info("✅ Scheduler parado")
    
    async def pause(self) -> None:
        """Pausa o scheduler (jobs não executam)."""
        if self._state != SchedulerState.RUNNING:
            return
        
        if self._scheduler:
            self._scheduler.pause()
        
        self._state = SchedulerState.PAUSED
        self.logger.info("Scheduler pausado")
    
    async def resume(self) -> None:
        """Resume o scheduler pausado."""
        if self._state != SchedulerState.PAUSED:
            return
        
        if self._scheduler:
            self._scheduler.resume()
        
        self._state = SchedulerState.RUNNING
        self.logger.info("Scheduler resumido")
    
    async def _run_job(self, job_id: str) -> Optional[JobResult]:
        """
        Executa um job específico.
        
        Args:
            job_id: ID do job a executar
            
        Returns:
            JobResult ou None se falhar
        """
        job = self._jobs.get(job_id)
        if not job:
            self.logger.error(f"Job não encontrado: {job_id}")
            return None
        
        if job.is_running:
            self.logger.warning(f"Job {job_id} já está em execução, ignorando")
            return None
        
        self.logger.info(f"▶️ Executando: {job_id}")
        
        try:
            result = await job.run()
            
            self._total_executions += 1
            self._last_execution = datetime.utcnow()
            
            if not result.success:
                self._total_errors += 1
            
            return result
            
        except Exception as e:
            self._total_errors += 1
            self.logger.error(f"Erro ao executar {job_id}: {e}")
            return None
    
    async def run_job_now(self, job_id: str) -> Optional[JobResult]:
        """
        Executa um job imediatamente (sob demanda).
        
        Args:
            job_id: ID do job
            
        Returns:
            JobResult ou None
        """
        return await self._run_job(job_id)
    
    def _on_job_executed(self, event: JobExecutionEvent) -> None:
        """Callback quando job é executado."""
        self.logger.debug(f"Job executado: {event.job_id}")
    
    def _on_job_error(self, event: JobExecutionEvent) -> None:
        """Callback quando job tem erro."""
        self.logger.error(
            f"Erro no job {event.job_id}: {event.exception}"
        )
    
    def _on_job_missed(self, event: JobExecutionEvent) -> None:
        """Callback quando job é perdido."""
        self.logger.warning(f"Job perdido: {event.job_id}")
    
    def get_job(self, job_id: str) -> Optional[BaseJob]:
        """Retorna instância de um job."""
        return self._jobs.get(job_id)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de um job específico."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        # Pega próxima execução do APScheduler
        next_run = None
        if self._scheduler:
            ap_job = self._scheduler.get_job(job_id)
            if ap_job and ap_job.next_run_time:
                next_run = ap_job.next_run_time.isoformat()
        
        status = job.get_status()
        status["next_run"] = next_run
        
        return status
    
    def get_all_jobs_status(self) -> Dict[str, Any]:
        """Retorna status de todos os jobs."""
        jobs_status = {}
        
        for job_id in self._jobs:
            jobs_status[job_id] = self.get_job_status(job_id)
        
        return jobs_status
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status geral do scheduler."""
        uptime = None
        if self._start_time:
            uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        return {
            "state": self._state.value,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "uptime_seconds": uptime,
            "total_jobs": len(self._jobs),
            "total_executions": self._total_executions,
            "total_errors": self._total_errors,
            "error_rate": (
                f"{(self._total_errors / self._total_executions * 100):.1f}%"
                if self._total_executions > 0 else "0%"
            ),
            "last_execution": (
                self._last_execution.isoformat()
                if self._last_execution else None
            ),
            "jobs": self.get_all_jobs_status(),
        }
    
    def get_job_history(self, job_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna histórico de execuções de um job."""
        job = self._jobs.get(job_id)
        if not job:
            return []
        
        return job.get_history(limit)
    
    @property
    def state(self) -> SchedulerState:
        """Retorna estado atual."""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """Retorna se está rodando."""
        return self._state == SchedulerState.RUNNING


# ===========================================
# Instância Global (Singleton)
# ===========================================

_scheduler: Optional[CryptoPulseScheduler] = None


async def get_scheduler() -> CryptoPulseScheduler:
    """
    Retorna instância do scheduler (singleton).
    
    Returns:
        CryptoPulseScheduler
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = CryptoPulseScheduler()
    return _scheduler


async def start_scheduler() -> CryptoPulseScheduler:
    """
    Inicia o scheduler global.
    
    Returns:
        CryptoPulseScheduler iniciado
    """
    scheduler = await get_scheduler()
    await scheduler.start()
    return scheduler


async def stop_scheduler() -> None:
    """Para o scheduler global."""
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None
