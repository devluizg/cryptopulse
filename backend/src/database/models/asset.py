"""
CryptoPulse - Asset Model
Representa uma criptomoeda monitorada pelo sistema
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.signal import AssetScore
    from src.database.models.whale_transaction import WhaleTransaction
    from src.database.models.exchange_flow import ExchangeFlow
    from src.database.models.alert import Alert
    from src.database.models.price_data import PriceData


class Asset(Base):
    """
    Modelo para criptomoedas monitoradas.
    
    Exemplos: BTC, ETH, SOL, etc.
    """
    
    __tablename__ = "assets"
    
    # ===========================================
    # Colunas Principais
    # ===========================================
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identificadores
    symbol: Mapped[str] = mapped_column(
        String(20), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Símbolo do ativo (ex: BTC, ETH)"
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Nome completo (ex: Bitcoin, Ethereum)"
    )
    
    # IDs externos para APIs
    coingecko_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="ID no CoinGecko (ex: bitcoin, ethereum)"
    )
    binance_symbol: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Par de trading na Binance (ex: BTCUSDT)"
    )
    
    # Configurações
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        comment="Se o ativo está sendo monitorado"
    )
    priority: Mapped[int] = mapped_column(
        Integer, 
        default=0,
        comment="Prioridade de monitoramento (maior = mais importante)"
    )
    
    # Metadados
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição do ativo"
    )
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL do logo"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # ===========================================
    # Relacionamentos
    # ===========================================
    
    scores: Mapped[List["AssetScore"]] = relationship(
        "AssetScore",
        back_populates="asset",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    whale_transactions: Mapped[List["WhaleTransaction"]] = relationship(
        "WhaleTransaction",
        back_populates="asset",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    exchange_flows: Mapped[List["ExchangeFlow"]] = relationship(
        "ExchangeFlow",
        back_populates="asset",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="asset",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    price_data: Mapped[List["PriceData"]] = relationship(
        "PriceData",
        back_populates="asset",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # ===========================================
    # Métodos
    # ===========================================
    
    def __repr__(self) -> str:
        return f"<Asset(symbol={self.symbol}, name={self.name})>"
    
    @property
    def display_name(self) -> str:
        """Retorna nome formatado para exibição"""
        return f"{self.name} ({self.symbol})"
