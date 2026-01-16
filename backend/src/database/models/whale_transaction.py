"""
CryptoPulse - Whale Transaction Model
Armazena transações grandes (baleias) detectadas
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey,
    Text, Index, BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.asset import Asset


class WhaleTransaction(Base):
    """
    Modelo para transações de baleias.
    
    Armazena grandes movimentações detectadas pelo Whale Alert
    ou outras fontes.
    """
    
    __tablename__ = "whale_transactions"
    
    __table_args__ = (
        Index('ix_whale_tx_asset_time', 'asset_id', 'timestamp'),
        Index('ix_whale_tx_type', 'transaction_type'),
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
    # Dados da Transação
    # ===========================================
    
    tx_hash: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="Hash da transação"
    )
    
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Quantidade do ativo"
    )
    
    amount_usd: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Valor em USD"
    )
    
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo: exchange_deposit, exchange_withdrawal, unknown_transfer, etc"
    )
    
    # ===========================================
    # Endereços
    # ===========================================
    
    from_address: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Endereço de origem"
    )
    
    from_owner: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Dono do endereço de origem (ex: binance, unknown)"
    )
    
    to_address: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Endereço de destino"
    )
    
    to_owner: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Dono do endereço de destino"
    )
    
    # ===========================================
    # Metadados
    # ===========================================
    
    blockchain: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Blockchain da transação"
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
        comment="Momento da transação"
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
        back_populates="whale_transactions"
    )
    
    # ===========================================
    # Métodos
    # ===========================================
    
    def __repr__(self) -> str:
        return f"<WhaleTransaction(asset_id={self.asset_id}, amount_usd=${self.amount_usd:,.0f}, type={self.transaction_type})>"
    
    @property
    def is_exchange_inflow(self) -> bool:
        """Verifica se é entrada em exchange"""
        return self.transaction_type == "exchange_deposit"
    
    @property
    def is_exchange_outflow(self) -> bool:
        """Verifica se é saída de exchange"""
        return self.transaction_type == "exchange_withdrawal"
