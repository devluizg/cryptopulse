"""
Modelo AssetScore - Scores calculados para cada ativo.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, 
    ForeignKey, Text, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..connection import Base


class AssetScore(Base):
    """
    Modelo para armazenar scores calculados.
    
    Cada registro representa um snapshot do score em um momento específico.
    """
    
    __tablename__ = "asset_scores"
    
    # Chave primária
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relacionamento com Asset
    asset_id = Column(
        Integer, 
        ForeignKey("assets.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Score principal (0-100)
    explosion_score = Column(Float, nullable=False, default=50.0)
    
    # Status derivado do score
    status = Column(
        String(20), 
        nullable=False, 
        default="low",
        index=True
    )  # 'high', 'attention', 'low'
    
    # Scores individuais dos indicadores (0-100)
    whale_accumulation_score = Column(Float, nullable=False, default=50.0)
    exchange_netflow_score = Column(Float, nullable=False, default=50.0)
    volume_anomaly_score = Column(Float, nullable=False, default=50.0)
    oi_pressure_score = Column(Float, nullable=False, default=50.0)
    narrative_momentum_score = Column(Float, nullable=False, default=50.0)
    
    # Dados de preço no momento do cálculo
    price_usd = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    
    # Detalhes do cálculo (JSONB com breakdown)
    calculation_details = Column(JSONB, nullable=True, default=dict)
    
    # Principais drivers do score
    main_drivers = Column(Text, nullable=True)
    
    # Timestamps
    calculated_at = Column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        index=True
    )
    
    # Relacionamento
    asset = relationship("Asset", back_populates="scores")
    
    # Índices compostos
    __table_args__ = (
        Index("ix_asset_scores_asset_calculated", "asset_id", "calculated_at"),
        Index("ix_asset_scores_status_score", "status", "explosion_score"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<AssetScore(id={self.id}, asset_id={self.asset_id}, "
            f"score={self.explosion_score}, status={self.status})>"
        )
    
    def is_high_score(self) -> bool:
        """Verifica se está em zona de explosão."""
        score: float = getattr(self, 'explosion_score', None) or 0.0
        status: str = getattr(self, 'status', None) or "low"
        return status == "high" or score >= 70
    
    def is_attention_score(self) -> bool:
        """Verifica se está em zona de atenção."""
        score: float = getattr(self, 'explosion_score', None) or 0.0
        status: str = getattr(self, 'status', None) or "low"
        return status == "attention" or (40 <= score < 70)
    
    def get_indicator_breakdown(self) -> Dict[str, float]:
        """Retorna breakdown dos indicadores."""
        def safe_float(attr_name: str, default: float = 50.0) -> float:
            """Converte para float de forma segura."""
            val = getattr(self, attr_name, None)
            if val is None:
                return default
            try:
                return float(val)
            except (TypeError, ValueError):
                return default
        
        return {
            "whale_accumulation": safe_float('whale_accumulation_score'),
            "exchange_netflow": safe_float('exchange_netflow_score'),
            "volume_anomaly": safe_float('volume_anomaly_score'),
            "oi_pressure": safe_float('oi_pressure_score'),
            "narrative_momentum": safe_float('narrative_momentum_score'),
        }
