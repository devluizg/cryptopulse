"""
CryptoPulse - Asset Schemas
Schemas Pydantic para Assets
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AssetBase(BaseModel):
    """Schema base para Asset"""
    symbol: str = Field(..., json_schema_extra={"example": "BTC"})
    name: str = Field(..., json_schema_extra={"example": "Bitcoin"})


class AssetResponse(AssetBase):
    """Schema de resposta para Asset"""
    id: int
    coingecko_id: Optional[str] = None
    binance_symbol: Optional[str] = None
    is_active: bool = True
    priority: int = 0
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScoreResponse(BaseModel):
    """Schema de resposta para Score"""
    id: int
    asset_id: int
    explosion_score: float = Field(..., ge=0, le=100)
    status: str = Field(..., json_schema_extra={"example": "attention"})
    
    # Componentes
    whale_accumulation_score: float = 0.0
    exchange_netflow_score: float = 0.0
    volume_anomaly_score: float = 0.0
    oi_pressure_score: float = 0.0
    narrative_momentum_score: float = 0.0
    
    # Contexto
    price_usd: Optional[float] = None
    price_change_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class AssetWithScoreResponse(AssetResponse):
    """Asset com score mais recente"""
    latest_score: Optional[ScoreResponse] = None


class AssetListResponse(BaseModel):
    """Lista de assets"""
    items: List[AssetWithScoreResponse]
    total: int
