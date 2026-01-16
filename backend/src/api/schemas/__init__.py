"""
CryptoPulse - API Schemas
"""

from src.api.schemas.asset_schema import (
    AssetBase,
    AssetResponse,
    AssetWithScoreResponse,
    AssetListResponse,
    ScoreResponse,
)
from src.api.schemas.signal_schema import (
    ScoreBase,
    ScoreCreate,
    ScoreDetail,
    ScoreWithAsset,
    ScoreHistoryResponse,
    DashboardResponse,
)
from src.api.schemas.alert_schema import (
    AlertBase,
    AlertCreate,
    AlertResponse,
    AlertWithAsset,
    AlertListResponse,
    AlertStatsResponse,
    MarkReadRequest,
)

__all__ = [
    "AssetBase",
    "AssetResponse",
    "AssetWithScoreResponse",
    "AssetListResponse",
    "ScoreResponse",
    "ScoreBase",
    "ScoreCreate",
    "ScoreDetail",
    "ScoreWithAsset",
    "ScoreHistoryResponse",
    "DashboardResponse",
    "AlertBase",
    "AlertCreate",
    "AlertResponse",
    "AlertWithAsset",
    "AlertListResponse",
    "AlertStatsResponse",
    "MarkReadRequest",
]
