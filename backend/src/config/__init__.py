"""
Módulo de configuração do CryptoPulse.
"""

from src.config.settings import settings, Settings
from src.config.api_keys import api_keys, APIKeys
from src.config.jobs_config import (
    JobConfig,
    JobPriority,
    SchedulerConfig,
    SCHEDULER_CONFIG,
    ALL_JOBS,
    PRICE_COLLECTION_JOB,
    WHALE_COLLECTION_JOB,
    NEWS_COLLECTION_JOB,
    OI_COLLECTION_JOB,
    SCORE_CALCULATION_JOB,
    ALERT_CHECK_JOB,
    DATA_CLEANUP_JOB,
    HEALTH_CHECK_JOB,
)

__all__ = [
    # Settings
    "settings",
    "Settings",
    "api_keys",
    "APIKeys",
    # Jobs
    "JobConfig",
    "JobPriority",
    "SchedulerConfig",
    "SCHEDULER_CONFIG",
    "ALL_JOBS",
    "PRICE_COLLECTION_JOB",
    "WHALE_COLLECTION_JOB",
    "NEWS_COLLECTION_JOB",
    "OI_COLLECTION_JOB",
    "SCORE_CALCULATION_JOB",
    "ALERT_CHECK_JOB",
    "DATA_CLEANUP_JOB",
    "HEALTH_CHECK_JOB",
]
