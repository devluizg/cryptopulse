"""
CryptoPulse - Alert Model
Armazena alertas gerados pelo sistema
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey,
    Text, Boolean, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.asset import Asset


class Alert(Base):
    """
    Modelo para alertas do sistema.
    
    Alertas são gerados quando:
    - Score ultrapassa threshold (70+)
    - Mudança brusca em score
    - Atividade anormal de baleias
    """
    
    __tablename__ = "alerts"
    
    __table_args__ = (
        Index('ix_alerts_asset_created', 'asset_id', 'created_at'),
        Index('ix_alerts_unread', 'is_read', 'created_at'),
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
    # Tipo e Severidade
    # ===========================================
    
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo: score_threshold, whale_activity, sudden_change, volume_spike"
    )
    
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="info",
        comment="Severidade: info, warning, critical"
    )
    
    # ===========================================
    # Conteúdo
    # ===========================================
    
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Título do alerta"
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mensagem detalhada"
    )
    
    # ===========================================
    # Dados de Contexto
    # ===========================================
    
    trigger_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Valor que disparou o alerta"
    )
    
    trigger_reason: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Detalhes do motivo em JSON"
    )
    
    score_at_trigger: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Score no momento do alerta"
    )
    
    price_at_trigger: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Preço no momento do alerta"
    )
    
    # ===========================================
    # Status
    # ===========================================
    
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se o alerta foi lido"
    )
    
    is_dismissed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se o alerta foi dispensado"
    )
    
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Momento em que foi lido"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
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
        back_populates="alerts"
    )
    
    # ===========================================
    # Métodos
    # ===========================================
    
    def __repr__(self) -> str:
        return f"<Alert(asset_id={self.asset_id}, type={self.alert_type}, severity={self.severity})>"
    
    def mark_as_read(self) -> None:
        """Marca o alerta como lido"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    @property
    def is_critical(self) -> bool:
        return self.severity == "critical"
    
    @property
    def is_warning(self) -> bool:
        return self.severity == "warning"
