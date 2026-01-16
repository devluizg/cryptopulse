"""
CryptoPulse - Metric Snapshot Model
Armazena snapshots históricos para análise
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Integer, Float, String, DateTime, Date, Index
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from src.database.connection import Base


class MetricSnapshot(Base):
    """
    Modelo para snapshots de métricas.
    
    Armazena um snapshot diário consolidado para
    análises históricas e comparações.
    """
    
    __tablename__ = "metric_snapshots"
    
    __table_args__ = (
        Index('ix_metric_symbol_date', 'symbol', 'snapshot_date', unique=True),
    )
    
    # ===========================================
    # Colunas Principais
    # ===========================================
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Símbolo do ativo"
    )
    
    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Data do snapshot"
    )
    
    # ===========================================
    # Scores
    # ===========================================
    
    explosion_score_open: Mapped[float] = mapped_column(
        Float, nullable=True, comment="Score no início do dia"
    )
    explosion_score_high: Mapped[float] = mapped_column(
        Float, nullable=True, comment="Score máximo do dia"
    )
    explosion_score_low: Mapped[float] = mapped_column(
        Float, nullable=True, comment="Score mínimo do dia"
    )
    explosion_score_close: Mapped[float] = mapped_column(
        Float, nullable=True, comment="Score no final do dia"
    )
    
    # ===========================================
    # Preço
    # ===========================================
    
    price_open: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_close: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_change_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # ===========================================
    # Volume
    # ===========================================
    
    volume_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # ===========================================
    # Whale Activity
    # ===========================================
    
    whale_transactions_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Número de transações de baleias"
    )
    whale_volume_total: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Volume total de baleias (USD)"
    )
    
    # ===========================================
    # Exchange Flow
    # ===========================================
    
    exchange_netflow_total: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Netflow total do dia"
    )
    
    # ===========================================
    # Alertas
    # ===========================================
    
    alerts_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Número de alertas gerados"
    )
    
    # ===========================================
    # Dados Completos
    # ===========================================
    
    full_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Dados completos em JSON"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # ===========================================
    # Métodos
    # ===========================================
    
    def __repr__(self) -> str:
        return f"<MetricSnapshot(symbol={self.symbol}, date={self.snapshot_date})>"
