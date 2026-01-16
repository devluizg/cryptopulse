"""
CryptoPulse Jobs Package.

Sistema de jobs agendados para:
- Coleta de dados (preços, whales, news, OI)
- Cálculo de scores
- Verificação de alertas
- Manutenção do sistema
"""

from src.jobs.base_job import BaseJob, JobResult, JobMetrics
from src.jobs.scheduler import (
    CryptoPulseScheduler,
    SchedulerState,
    get_scheduler,
    start_scheduler,
    stop_scheduler,
)
from src.jobs.data_collection_job import (
    PriceCollectionJob,
    WhaleCollectionJob,
    NewsCollectionJob,
    OpenInterestCollectionJob,
    FullDataCollectionJob,
)
from src.jobs.score_calculation_job import (
    ScoreCalculationJob,
    SingleAssetScoreJob,
)
from src.jobs.alert_check_job import (
    AlertCheckJob,
    DataCleanupJob,
    HealthCheckJob,
)

__all__ = [
    # Base
    "BaseJob",
    "JobResult",
    "JobMetrics",
    # Scheduler
    "CryptoPulseScheduler",
    "SchedulerState",
    "get_scheduler",
    "start_scheduler",
    "stop_scheduler",
    # Data Collection Jobs
    "PriceCollectionJob",
    "WhaleCollectionJob",
    "NewsCollectionJob",
    "OpenInterestCollectionJob",
    "FullDataCollectionJob",
    # Score Jobs
    "ScoreCalculationJob",
    "SingleAssetScoreJob",
    # Alert Jobs
    "AlertCheckJob",
    "DataCleanupJob",
    "HealthCheckJob",
]
