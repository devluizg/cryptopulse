"""
CryptoPulse - Narrative Event Model
Armazena notícias e eventos relevantes do mercado
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey,
    Text, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from src.database.connection import Base


class NarrativeEvent(Base):
    """
    Modelo para eventos de narrativa.
    
    Armazena notícias, anúncios e eventos que podem
    impactar o mercado cripto.
    """
    
    __tablename__ = "narrative_events"
    
    __table_args__ = (
        Index('ix_narrative_published', 'published_at'),
        Index('ix_narrative_sentiment', 'sentiment_score'),
    )
    
    # ===========================================
    # Colunas Principais
    # ===========================================
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Pode ou não estar associado a um ativo específico
    asset_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # ===========================================
    # Conteúdo
    # ===========================================
    
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Título da notícia/evento"
    )
    
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Resumo do conteúdo"
    )
    
    url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="URL da fonte"
    )
    
    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Fonte: cryptopanic, twitter, manual, etc"
    )
    
    # ===========================================
    # Classificação
    # ===========================================
    
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="news",
        comment="Tipo: news, announcement, regulation, hack, listing, etc"
    )
    
    sentiment: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="neutral",
        comment="Sentimento: positive, negative, neutral"
    )
    
    sentiment_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Score de sentimento (-1 a 1)"
    )
    
    importance: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="low",
        comment="Importância: low, medium, high, critical"
    )
    
    # ===========================================
    # Metadados
    # ===========================================
    
    # Tags relacionadas (ex: ["btc", "etf", "sec"])
    tags: Mapped[Optional[list]] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
        comment="Tags relacionadas"
    )
    
    # Ativos mencionados
    mentioned_assets: Mapped[Optional[list]] = mapped_column(
        ARRAY(String(20)),
        nullable=True,
        comment="Símbolos de ativos mencionados"
    )
    
    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Dados brutos da API"
    )
    
    # Timestamps
    published_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        comment="Data de publicação"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # ===========================================
    # Métodos
    # ===========================================
    
    def __repr__(self) -> str:
        return f"<NarrativeEvent(title={self.title[:50]}..., sentiment={self.sentiment})>"
    
    @property
    def is_positive(self) -> bool:
        return self.sentiment == "positive"
    
    @property
    def is_negative(self) -> bool:
        return self.sentiment == "negative"
    
    @property
    def is_important(self) -> bool:
        return self.importance in ["high", "critical"]
