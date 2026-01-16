"""
CryptoPulse - Signal/Score Model
Armazena os scores calculados para cada ativo
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey, 
    Text, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.asset import Asset


class AssetScore(Base):
    """
    Modelo para scores calculados.
    
    Cada registro representa o score de um ativo em um momento específico.
    O explosion_score é o score principal (0-100).
    """
    
    __tablename__ = "asset_scores"
    
    # ===========================================
    # Índices compostos
    # ===========================================
    
    __table_args__ = (
        Index('ix_asset_scores_asset_timestamp', 'asset_id', 'calculated_at'),
        Index('ix_asset_scores_explosion', 'explosion_score'),
    )
    
    # ===========================================
    # Colunas Principais
    # ===========================================
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Relacionamento com Asset
    asset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # ===========================================
    # Score Principal
    # ===========================================
    
    explosion_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Score de explosão (0-100)"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="low",
        comment="Status: low, attention, high"
    )
    
    # ===========================================
    # Componentes do Score
    # ===========================================
    
    whale_accumulation_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Score de acumulação de baleias (0-100)"
    )
    
    exchange_netflow_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Score de fluxo líquido de exchanges (0-100)"
    )
    
    volume_anomaly_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Score de anomalia de volume (0-100)"
    )
    
    oi_pressure_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Score de pressão de Open Interest (0-100)"
    )
    
    narrative_momentum_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Score de momentum de narrativa (0-100)"
    )
    
    # ===========================================
    # Dados de Contexto
    # ===========================================
    
    price_usd: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Preço em USD no momento do cálculo"
    )
    
    price_change_24h: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Variação de preço em 24h (%)"
    )
    
    volume_24h: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Volume em 24h (USD)"
    )
    
    # ===========================================
    # Metadados do Cálculo
    # ===========================================
    
    calculation_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Detalhes do cálculo em JSON"
    )
    
    main_drivers: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Principais fatores do score"
    )
    
    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # ===========================================
    # Relacionamentos
    # ===========================================
    
    asset: Mapped["Asset"] = relationship(
        "Asset",
        back_populates="scores"
    )
    
    # ===========================================
    # Métodos
    # ===========================================
    
    def __repr__(self) -> str:
        return f"<AssetScore(asset_id={self.asset_id}, score={self.explosion_score}, status={self.status})>"
    
    @property
    def is_high(self) -> bool:
        return self.status == "high"
    
    @property
    def is_attention(self) -> bool:
        return self.status == "attention"
    
    @property
    def score_breakdown(self) -> dict:
        """Retorna breakdown dos componentes"""
        return {
            "whale_accumulation": self.whale_accumulation_score,
            "exchange_netflow": self.exchange_netflow_score,
            "volume_anomaly": self.volume_anomaly_score,
            "oi_pressure": self.oi_pressure_score,
            "narrative_momentum": self.narrative_momentum_score,
        }
