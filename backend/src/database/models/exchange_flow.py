"""
CryptoPulse - Exchange Flow Model
Armazena dados de fluxo de entrada/saída de exchanges
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.asset import Asset


class ExchangeFlow(Base):
    """
    Modelo para fluxo de exchanges.
    
    Armazena dados agregados de entrada/saída de criptomoedas
    em exchanges (inflow/outflow).
    """
    
    __tablename__ = "exchange_flows"
    
    __table_args__ = (
        Index('ix_exchange_flow_asset_time', 'asset_id', 'timestamp'),
    )
    
    # ===========================================
    # Colunas Principais
    # ===========================================
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    asset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # ===========================================
    # Dados de Fluxo
    # ===========================================
    
    inflow: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Volume entrando em exchanges (USD)"
    )
    
    outflow: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Volume saindo de exchanges (USD)"
    )
    
    netflow: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Fluxo líquido (inflow - outflow). Negativo = saída"
    )
    
    # ===========================================
    # Contexto
    # ===========================================
    
    exchange: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="all",
        comment="Exchange específica ou 'all' para agregado"
    )
    
    timeframe: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="24h",
        comment="Período: 1h, 24h, 7d"
    )
    
    # Metadados
    source: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Fonte dos dados: glassnode, cryptoquant, etc"
    )
    
    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Dados brutos da API"
    )
    
    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        comment="Momento da medição"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # ===========================================
    # Relacionamentos
    # ===========================================
    
    asset: Mapped["Asset"] = relationship(
        "Asset",
        back_populates="exchange_flows"
    )
    
    # ===========================================
    # Métodos
    # ===========================================
    
    def __repr__(self) -> str:
        return f"<ExchangeFlow(asset_id={self.asset_id}, netflow=${self.netflow:,.0f})>"
    
    @property
    def is_bullish(self) -> bool:
        """Netflow negativo = saída de exchange = bullish"""
        return self.netflow < 0
    
    @property
    def is_bearish(self) -> bool:
        """Netflow positivo = entrada em exchange = bearish"""
        return self.netflow > 0
