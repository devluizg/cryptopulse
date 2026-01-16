"""
Configurações dos Jobs Agendados.

Define intervalos, timeouts e comportamentos dos jobs.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class JobPriority(str, Enum):
    """Prioridade dos jobs."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class JobConfig:
    """Configuração de um job individual."""
    
    # Identificação
    job_id: str
    name: str
    description: str
    
    # Agendamento (em segundos)
    interval_seconds: int
    
    # Comportamento
    enabled: bool = True
    priority: JobPriority = JobPriority.NORMAL
    max_instances: int = 1  # Quantas instâncias simultâneas permitir
    coalesce: bool = True   # Agrupa execuções atrasadas
    misfire_grace_time: int = 60  # Tempo de tolerância para execuções perdidas
    
    # Timeouts
    timeout_seconds: int = 300  # 5 minutos padrão
    
    # Retry
    max_retries: int = 3
    retry_delay_seconds: int = 30
    
    # Metadados
    tags: list = field(default_factory=list)


# ===========================================
# Configurações Padrão dos Jobs
# ===========================================

PRICE_COLLECTION_JOB = JobConfig(
    job_id="price_collection",
    name="Coleta de Preços",
    description="Coleta preços de todas as criptomoedas monitoradas",
    interval_seconds=60,  # 1 minuto
    priority=JobPriority.HIGH,
    timeout_seconds=120,
    max_retries=3,
    tags=["collector", "prices"],
)

WHALE_COLLECTION_JOB = JobConfig(
    job_id="whale_collection",
    name="Coleta de Whales",
    description="Coleta transações de whales via Etherscan/Blockchain",
    interval_seconds=300,  # 5 minutos
    priority=JobPriority.NORMAL,
    timeout_seconds=180,
    max_retries=2,
    tags=["collector", "whales"],
)

NEWS_COLLECTION_JOB = JobConfig(
    job_id="news_collection",
    name="Coleta de Notícias",
    description="Coleta notícias e eventos do mercado",
    interval_seconds=600,  # 10 minutos
    priority=JobPriority.LOW,
    timeout_seconds=120,
    max_retries=2,
    tags=["collector", "news"],
)

OI_COLLECTION_JOB = JobConfig(
    job_id="oi_collection",
    name="Coleta de Open Interest",
    description="Coleta dados de derivativos da Binance",
    interval_seconds=300,  # 5 minutos
    priority=JobPriority.NORMAL,
    timeout_seconds=120,
    max_retries=2,
    tags=["collector", "derivatives"],
)

KLINE_COLLECTION_JOB = JobConfig(
    job_id="kline_collection",
    name="Coleta de Klines (OHLCV)",
    description="Coleta candles de 1h da Binance para análise de volume",
    interval_seconds=300,  # 5 minutos
    priority=JobPriority.NORMAL,
    timeout_seconds=180,
    max_retries=2,
    tags=["collector", "klines", "volume"],
)

SCORE_CALCULATION_JOB = JobConfig(
    job_id="score_calculation",
    name="Cálculo de Scores",
    description="Calcula Explosion Score para todos os ativos",
    interval_seconds=300,  # 5 minutos
    priority=JobPriority.HIGH,
    timeout_seconds=300,
    max_retries=2,
    tags=["engine", "scores"],
)

ALERT_CHECK_JOB = JobConfig(
    job_id="alert_check",
    name="Verificação de Alertas",
    description="Verifica condições e gera alertas",
    interval_seconds=60,  # 1 minuto
    priority=JobPriority.HIGH,
    timeout_seconds=120,
    max_retries=2,
    tags=["alerts"],
)

DATA_CLEANUP_JOB = JobConfig(
    job_id="data_cleanup",
    name="Limpeza de Dados",
    description="Remove dados antigos do sistema",
    interval_seconds=86400,  # 24 horas
    priority=JobPriority.LOW,
    timeout_seconds=600,
    max_retries=1,
    tags=["maintenance"],
)

HEALTH_CHECK_JOB = JobConfig(
    job_id="health_check",
    name="Health Check",
    description="Verifica saúde dos coletores e serviços",
    interval_seconds=120,  # 2 minutos
    priority=JobPriority.NORMAL,
    timeout_seconds=60,
    max_retries=1,
    tags=["monitoring"],
)


# ===========================================
# Dicionário de todos os jobs
# ===========================================

ALL_JOBS: Dict[str, JobConfig] = {
    "price_collection": PRICE_COLLECTION_JOB,
    "whale_collection": WHALE_COLLECTION_JOB,
    "news_collection": NEWS_COLLECTION_JOB,
    "oi_collection": OI_COLLECTION_JOB,
    "kline_collection": KLINE_COLLECTION_JOB,
    "score_calculation": SCORE_CALCULATION_JOB,
    "alert_check": ALERT_CHECK_JOB,
    "data_cleanup": DATA_CLEANUP_JOB,
    "health_check": HEALTH_CHECK_JOB,
}


# ===========================================
# Configurações Gerais do Scheduler
# ===========================================

@dataclass
class SchedulerConfig:
    """Configuração geral do scheduler."""
    
    # Thread pool
    max_workers: int = 10
    
    # Comportamento
    daemon: bool = True
    
    # Timezone
    timezone: str = "UTC"
    
    # Jobs a habilitar por padrão
    enabled_jobs: list = field(default_factory=lambda: [
        "price_collection",
        "whale_collection",
        "news_collection",
        "oi_collection",
        "kline_collection",
        "score_calculation",
        "alert_check",
        "health_check",
    ])
    
    # Delays iniciais (para não sobrecarregar no startup)
    startup_delay_seconds: int = 10
    job_stagger_seconds: int = 5  # Intervalo entre início de cada job


SCHEDULER_CONFIG = SchedulerConfig()
