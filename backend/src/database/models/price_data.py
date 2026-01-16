"""
CryptoPulse - Price Data Model
Armazena dados OHLCV de preços
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey, Index, BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.asset import Asset


class PriceData(Base):
    """
    Modelo para dados de preço OHLCV.
    
    Armazena candles de preço para análise de volume
    e detecção de anomalias.
    """
    
    __tablename__ = "price_data"
    
    __table_args__ = (
        Index('ix_price_asset_time', 'asset_id', 'timestamp'),
        Index('ix_price_timeframe', 'timeframe', 'timestamp'),
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
    # OHLCV Data
    # ===========================================
    
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False, comment="Volume em USD")
    
    # ===========================================
    # Metadados
    # ===========================================
    
    timeframe: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="1h",
        comment="Timeframe: 1m, 5m, 15m, 1h, 4h, 1d"
    )
    
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="binance",
        comment="Fonte: binance, coingecko, etc"
    )
    
    # Timestamp do candle
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        comment="Abertura do candle"
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
        back_populates="price_data"
    )
    
    # ===========================================
    # Métodos
    # ===========================================
    
    def __repr__(self) -> str:
        return f"<PriceData(asset_id={self.asset_id}, close={self.close}, time={self.timestamp})>"
    
    @property
    def change_pct(self) -> float:
        """Variação percentual do candle"""
        if self.open == 0:
            return 0
        return ((self.close - self.open) / self.open) * 100
    
    @property
    def is_green(self) -> bool:
        """Candle de alta"""
        return self.close >= self.open
    
    @property
    def is_red(self) -> bool:
        """Candle de baixa"""
        return self.close < self.open
