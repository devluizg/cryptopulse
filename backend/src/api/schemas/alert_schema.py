"""
CryptoPulse - Alert Schemas
Schemas Pydantic para Alerts
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AlertBase(BaseModel):
    """Schema base para Alert"""
    alert_type: str = Field(..., json_schema_extra={"example": "score_threshold"})
    severity: str = Field(..., json_schema_extra={"example": "warning"})
    title: str
    message: str


class AlertCreate(AlertBase):
    """Schema para criar Alert"""
    asset_id: int
    trigger_value: Optional[float] = None
    trigger_reason: Optional[Dict[str, Any]] = None
    score_at_trigger: Optional[float] = None
    price_at_trigger: Optional[float] = None


class AlertResponse(AlertBase):
    """Schema de resposta para Alert"""
    id: int
    asset_id: int
    trigger_value: Optional[float] = None
    trigger_reason: Optional[Dict[str, Any]] = None
    score_at_trigger: Optional[float] = None
    price_at_trigger: Optional[float] = None
    is_read: bool = False
    is_dismissed: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertWithAsset(AlertResponse):
    """Alert com informações do asset"""
    symbol: str
    asset_name: str


class AlertListResponse(BaseModel):
    """Lista de alerts"""
    items: List[AlertWithAsset]
    total: int
    unread_count: int


class AlertStatsResponse(BaseModel):
    """Estatísticas de alerts"""
    total: int
    unread: int
    by_severity: Dict[str, int]
    today_count: int


class MarkReadRequest(BaseModel):
    """Request para marcar alertas como lidos"""
    alert_ids: List[int]
