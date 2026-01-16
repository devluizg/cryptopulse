"""
CryptoPulse - Signal Schemas
Schemas Pydantic para Signals/Scores
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScoreBase(BaseModel):
    """Schema base para Score"""
    explosion_score: float = Field(..., ge=0, le=100)
    status: str


class ScoreCreate(ScoreBase):
    """Schema para criar Score"""
    asset_id: int
    whale_accumulation_score: float = 0.0
    exchange_netflow_score: float = 0.0
    volume_anomaly_score: float = 0.0
    oi_pressure_score: float = 0.0
    narrative_momentum_score: float = 0.0
    price_usd: Optional[float] = None
    price_change_24h: Optional[float] = None
    volume_24h: Optional[float] = None


class ScoreDetail(ScoreBase):
    """Schema detalhado de Score"""
    id: int
    asset_id: int
    
    # Componentes do score
    whale_accumulation_score: float
    exchange_netflow_score: float
    volume_anomaly_score: float
    oi_pressure_score: float
    narrative_momentum_score: float
    
    # Contexto de mercado
    price_usd: Optional[float] = None
    price_change_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    
    # Detalhes
    calculation_details: Optional[Dict[str, Any]] = None
    main_drivers: Optional[str] = None
    
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class ScoreWithAsset(ScoreDetail):
    """Score com informações do asset"""
    symbol: str
    asset_name: str


class ScoreHistoryResponse(BaseModel):
    """Histórico de scores"""
    symbol: str
    scores: List[ScoreDetail]
    count: int


class DashboardResponse(BaseModel):
    """Resposta do dashboard principal"""
    total_assets: int
    high_count: int
    attention_count: int
    low_count: int
    assets: List[ScoreWithAsset]
    updated_at: datetime
