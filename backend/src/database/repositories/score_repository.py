"""
Repositório para operações com AssetScore.
"""

from typing import List, Optional, Dict, Any, cast
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from .base_repository import BaseRepository
from ..models import AssetScore, Asset


class ScoreRepository(BaseRepository[AssetScore]):
    """Repositório para operações com AssetScore."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(AssetScore, session)
    
    async def get_latest_by_asset(self, asset_id: int) -> Optional[AssetScore]:
        """Retorna o score mais recente de um ativo."""
        query = (
            select(AssetScore)
            .where(AssetScore.asset_id == asset_id)
            .order_by(desc(AssetScore.calculated_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_latest_by_symbol(self, symbol: str) -> Optional[AssetScore]:
        """Retorna o score mais recente por símbolo do ativo."""
        query = (
            select(AssetScore)
            .join(Asset)
            .where(Asset.symbol == symbol.upper())
            .order_by(desc(AssetScore.calculated_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_latest(self) -> List[AssetScore]:
        """Retorna o score mais recente de cada ativo."""
        subquery = (
            select(
                AssetScore.asset_id,
                func.max(AssetScore.calculated_at).label("max_date")
            )
            .group_by(AssetScore.asset_id)
            .subquery()
        )
        
        query = (
            select(AssetScore)
            .join(
                subquery,
                and_(
                    AssetScore.asset_id == subquery.c.asset_id,
                    AssetScore.calculated_at == subquery.c.max_date
                )
            )
            .order_by(desc(AssetScore.explosion_score))
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_history(
        self, 
        asset_id: int, 
        hours: int = 24,
        limit: int = 100
    ) -> List[AssetScore]:
        """Retorna histórico de scores de um ativo."""
        since = datetime.utcnow() - timedelta(hours=hours)
        query = (
            select(AssetScore)
            .where(
                and_(
                    AssetScore.asset_id == asset_id,
                    AssetScore.calculated_at >= since
                )
            )
            .order_by(desc(AssetScore.calculated_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_high_scores(self, threshold: float = 70.0) -> List[AssetScore]:
        """Retorna scores acima do threshold (zona de explosão)."""
        subquery = (
            select(
                AssetScore.asset_id,
                func.max(AssetScore.calculated_at).label("max_date")
            )
            .group_by(AssetScore.asset_id)
            .subquery()
        )
        
        query = (
            select(AssetScore)
            .join(
                subquery,
                and_(
                    AssetScore.asset_id == subquery.c.asset_id,
                    AssetScore.calculated_at == subquery.c.max_date
                )
            )
            .where(AssetScore.explosion_score >= threshold)
            .order_by(desc(AssetScore.explosion_score))
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_status(self, status: str) -> List[AssetScore]:
        """Retorna scores mais recentes com um status específico."""
        subquery = (
            select(
                AssetScore.asset_id,
                func.max(AssetScore.calculated_at).label("max_date")
            )
            .group_by(AssetScore.asset_id)
            .subquery()
        )
        
        query = (
            select(AssetScore)
            .join(
                subquery,
                and_(
                    AssetScore.asset_id == subquery.c.asset_id,
                    AssetScore.calculated_at == subquery.c.max_date
                )
            )
            .where(AssetScore.status == status)
            .order_by(desc(AssetScore.explosion_score))
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_avg_score(self, asset_id: int, hours: int = 24) -> Optional[float]:
        """Retorna a média de scores nas últimas N horas."""
        since = datetime.utcnow() - timedelta(hours=hours)
        query = (
            select(func.avg(AssetScore.explosion_score))
            .where(
                and_(
                    AssetScore.asset_id == asset_id,
                    AssetScore.calculated_at >= since
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_max_score(self, asset_id: int, hours: int = 24) -> Optional[float]:
        """Retorna o score máximo nas últimas N horas."""
        since = datetime.utcnow() - timedelta(hours=hours)
        query = (
            select(func.max(AssetScore.explosion_score))
            .where(
                and_(
                    AssetScore.asset_id == asset_id,
                    AssetScore.calculated_at >= since
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def count_by_status(self) -> Dict[str, int]:
        """Conta scores mais recentes por status."""
        latest = await self.get_all_latest()
        counts = {"high": 0, "attention": 0, "low": 0}
        for score in latest:
            if score.status in counts:
                counts[score.status] += 1
        return counts
    
    async def create_score(
        self,
        asset_id: int,
        explosion_score: float,
        status: str,
        whale_accumulation_score: float = 50.0,
        exchange_netflow_score: float = 50.0,
        volume_anomaly_score: float = 50.0,
        oi_pressure_score: float = 50.0,
        narrative_momentum_score: float = 50.0,
        price_usd: Optional[float] = None,
        price_change_24h: Optional[float] = None,
        volume_24h: Optional[float] = None,
        calculation_details: Optional[Dict[str, Any]] = None,
        main_drivers: Optional[str] = None,
    ) -> AssetScore:
        """
        Cria um novo score.
        
        Args:
            asset_id: ID do ativo
            explosion_score: Score final (0-100)
            status: Status ('high', 'attention', 'low')
            whale_accumulation_score: Score do indicador de whales
            exchange_netflow_score: Score do indicador de netflow
            volume_anomaly_score: Score do indicador de volume
            oi_pressure_score: Score do indicador de OI
            narrative_momentum_score: Score do indicador de narrativa
            price_usd: Preço atual em USD
            price_change_24h: Variação 24h em %
            volume_24h: Volume 24h em USD
            calculation_details: Detalhes do cálculo (JSON)
            main_drivers: Principais fatores do score
            
        Returns:
            AssetScore criado
        """
        score = AssetScore(
            asset_id=asset_id,
            explosion_score=explosion_score,
            status=status,
            whale_accumulation_score=whale_accumulation_score,
            exchange_netflow_score=exchange_netflow_score,
            volume_anomaly_score=volume_anomaly_score,
            oi_pressure_score=oi_pressure_score,
            narrative_momentum_score=narrative_momentum_score,
            price_usd=price_usd,
            price_change_24h=price_change_24h,
            volume_24h=volume_24h,
            calculation_details=calculation_details or {},
            main_drivers=main_drivers,
            calculated_at=datetime.utcnow(),
        )
        
        self.session.add(score)
        await self.session.flush()
        
        logger.debug(f"Score criado: asset_id={asset_id}, score={explosion_score:.1f}, price=${price_usd or 0:.2f}")
        return score
    
    async def delete_old_scores(self, days: int = 30) -> int:
        """Remove scores mais antigos que N dias."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = delete(AssetScore).where(AssetScore.calculated_at < cutoff)
        result = await self.session.execute(query)
        return cast(int, result.rowcount)
