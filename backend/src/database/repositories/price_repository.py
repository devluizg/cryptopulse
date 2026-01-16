"""
CryptoPulse - Price Data Repository
Operações de banco para dados de preço
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import PriceData, Asset
from src.database.repositories.base_repository import BaseRepository


class PriceRepository(BaseRepository[PriceData]):
    """Repositório para operações com PriceData."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(PriceData, session)
    
    # ===========================================
    # Buscar preços
    # ===========================================
    
    async def get_latest(self, asset_id: int) -> Optional[PriceData]:
        """Retorna o preço mais recente de um ativo."""
        result = await self.session.execute(
            select(PriceData)
            .where(PriceData.asset_id == asset_id)
            .order_by(desc(PriceData.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_latest_by_symbol(self, symbol: str) -> Optional[PriceData]:
        """Retorna o preço mais recente pelo símbolo."""
        result = await self.session.execute(
            select(PriceData)
            .join(Asset)
            .where(Asset.symbol == symbol.upper())
            .order_by(desc(PriceData.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_history(
        self, 
        asset_id: int, 
        hours: int = 24,
        timeframe: str = "1h"
    ) -> List[PriceData]:
        """Retorna histórico de preços."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(PriceData)
            .where(
                and_(
                    PriceData.asset_id == asset_id,
                    PriceData.timestamp >= since,
                    PriceData.timeframe == timeframe
                )
            )
            .order_by(PriceData.timestamp)
        )
        return list(result.scalars().all())
    
    async def get_ohlcv(
        self, 
        asset_id: int,
        start: datetime,
        end: datetime,
        timeframe: str = "1h"
    ) -> List[PriceData]:
        """Retorna dados OHLCV em um período."""
        result = await self.session.execute(
            select(PriceData)
            .where(
                and_(
                    PriceData.asset_id == asset_id,
                    PriceData.timestamp >= start,
                    PriceData.timestamp <= end,
                    PriceData.timeframe == timeframe
                )
            )
            .order_by(PriceData.timestamp)
        )
        return list(result.scalars().all())
    
    # ===========================================
    # Estatísticas
    # ===========================================
    
    async def get_avg_volume(
        self, 
        asset_id: int, 
        days: int = 20
    ) -> float:
        """Retorna volume médio em USD."""
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await self.session.execute(
            select(func.avg(PriceData.volume))
            .where(
                and_(
                    PriceData.asset_id == asset_id,
                    PriceData.timestamp >= since,
                    PriceData.timeframe == "1d"
                )
            )
        )
        return result.scalar() or 0.0
    
    async def get_volume_std(
        self, 
        asset_id: int, 
        days: int = 20
    ) -> float:
        """Retorna desvio padrão do volume."""
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await self.session.execute(
            select(func.stddev(PriceData.volume))
            .where(
                and_(
                    PriceData.asset_id == asset_id,
                    PriceData.timestamp >= since,
                    PriceData.timeframe == "1d"
                )
            )
        )
        return result.scalar() or 0.0
    
    async def get_price_change(
        self, 
        asset_id: int, 
        hours: int = 24
    ) -> Optional[float]:
        """Calcula variação de preço em percentual."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Preço antigo
        old_result = await self.session.execute(
            select(PriceData.close)
            .where(
                and_(
                    PriceData.asset_id == asset_id,
                    PriceData.timestamp >= since
                )
            )
            .order_by(PriceData.timestamp)
            .limit(1)
        )
        old_price = old_result.scalar()
        
        # Preço atual
        current = await self.get_latest(asset_id)
        
        if old_price and current and old_price > 0:
            return ((current.close - old_price) / old_price) * 100
        return None
    
    async def get_high_low(
        self, 
        asset_id: int, 
        hours: int = 24
    ) -> dict:
        """Retorna máxima e mínima no período."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(
                func.max(PriceData.high),
                func.min(PriceData.low)
            )
            .where(
                and_(
                    PriceData.asset_id == asset_id,
                    PriceData.timestamp >= since
                )
            )
        )
        row = result.first()
        
        return {
            "high": row[0] if row else None,
            "low": row[1] if row else None
        }
    
    # ===========================================
    # Criação
    # ===========================================
    
    async def create_price(
        self,
        asset_id: int,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float,
        timestamp: datetime,
        timeframe: str = "1h",
        source: str = "binance"
    ) -> PriceData:
        """Cria um novo registro de preço."""
        # Nota: o modelo usa 'open', 'high', 'low', 'close' (não open_price, etc)
        price = PriceData(
            asset_id=asset_id,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume,
            timestamp=timestamp,
            timeframe=timeframe,
            source=source
        )
        self.session.add(price)
        await self.session.flush()
        return price
    
    async def upsert_price(
        self,
        asset_id: int,
        timestamp: datetime,
        timeframe: str,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: float,
        source: str = "binance"
    ) -> PriceData:
        """
        Cria ou atualiza registro de preço.
        
        Nota: aceita open_price, high_price, etc por conveniência,
        mas internamente usa os nomes do modelo (open, high, etc)
        """
        # Verifica se já existe
        result = await self.session.execute(
            select(PriceData)
            .where(
                and_(
                    PriceData.asset_id == asset_id,
                    PriceData.timestamp == timestamp,
                    PriceData.timeframe == timeframe
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Atualiza existente
            existing.open = open_price
            existing.high = high_price
            existing.low = low_price
            existing.close = close_price
            existing.volume = volume
            existing.source = source
            await self.session.flush()
            return existing
        else:
            # Cria novo
            return await self.create_price(
                asset_id=asset_id,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume,
                timestamp=timestamp,
                timeframe=timeframe,
                source=source
            )
