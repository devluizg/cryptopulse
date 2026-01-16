"""
CryptoPulse - Asset Repository
Operações de banco para ativos (criptomoedas)
"""

from typing import List, Optional, cast
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Asset, AssetScore
from src.database.repositories.base_repository import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """Repositório para operações com Asset."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Asset, session)
    
    # ===========================================
    # Buscas específicas
    # ===========================================
    
    async def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        """Busca ativo por símbolo (BTC, ETH, etc)."""
        result = await self.session.execute(
            select(Asset).where(Asset.symbol == symbol.upper())
        )
        return result.scalar_one_or_none()
    
    async def get_by_coingecko_id(self, coingecko_id: str) -> Optional[Asset]:
        """Busca ativo por ID do CoinGecko."""
        result = await self.session.execute(
            select(Asset).where(Asset.coingecko_id == coingecko_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_assets(self) -> List[Asset]:
        """Retorna apenas ativos ativos, ordenados por prioridade."""
        result = await self.session.execute(
            select(Asset)
            .where(Asset.is_active == True)
            .order_by(Asset.priority.desc())
        )
        return list(result.scalars().all())
    
    async def get_symbols(self, active_only: bool = True) -> List[str]:
        """Retorna lista de símbolos."""
        query = select(Asset.symbol)
        if active_only:
            query = query.where(Asset.is_active == True)
        query = query.order_by(Asset.priority.desc())
        
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def get_binance_symbols(self) -> List[str]:
        """Retorna símbolos da Binance para ativos ativos."""
        result = await self.session.execute(
            select(Asset.binance_symbol)
            .where(Asset.is_active == True)
            .where(Asset.binance_symbol.isnot(None))
        )
        return [row[0] for row in result.fetchall()]
    
    # ===========================================
    # Com relacionamentos
    # ===========================================
    
    async def get_with_latest_score(self, symbol: str) -> Optional[Asset]:
        """Busca ativo com seu score mais recente."""
        result = await self.session.execute(
            select(Asset)
            .options(selectinload(Asset.scores))
            .where(Asset.symbol == symbol.upper())
        )
        return result.scalar_one_or_none()
    
    async def get_all_with_scores(self) -> List[Asset]:
        """Retorna todos ativos ativos com scores."""
        result = await self.session.execute(
            select(Asset)
            .options(selectinload(Asset.scores))
            .where(Asset.is_active == True)
            .order_by(Asset.priority.desc())
        )
        return list(result.scalars().all())
    
    # ===========================================
    # Atualizações
    # ===========================================
    
    async def activate(self, symbol: str) -> bool:
        """Ativa um ativo."""
        result = await self.session.execute(
            update(Asset)
            .where(Asset.symbol == symbol.upper())
            .values(is_active=True)
        )
        await self.session.flush()
        return cast(int, result.rowcount) > 0
    
    async def deactivate(self, symbol: str) -> bool:
        """Desativa um ativo."""
        result = await self.session.execute(
            update(Asset)
            .where(Asset.symbol == symbol.upper())
            .values(is_active=False)
        )
        await self.session.flush()
        return cast(int, result.rowcount) > 0
    
    async def update_priority(self, symbol: str, priority: int) -> bool:
        """Atualiza prioridade de um ativo."""
        result = await self.session.execute(
            update(Asset)
            .where(Asset.symbol == symbol.upper())
            .values(priority=priority)
        )
        await self.session.flush()
        return cast(int, result.rowcount) > 0
    
    # ===========================================
    # Utilitários
    # ===========================================
    
    async def symbol_exists(self, symbol: str) -> bool:
        """Verifica se símbolo existe."""
        asset = await self.get_by_symbol(symbol)
        return asset is not None
    
    async def get_id_by_symbol(self, symbol: str) -> Optional[int]:
        """Retorna ID do ativo pelo símbolo."""
        result = await self.session.execute(
            select(Asset.id).where(Asset.symbol == symbol.upper())
        )
        row = result.first()
        return row[0] if row else None
    
    async def get_symbol_id_map(self) -> dict:
        """Retorna mapa de símbolo -> ID."""
        result = await self.session.execute(
            select(Asset.symbol, Asset.id).where(Asset.is_active == True)
        )
        return {row[0]: row[1] for row in result.fetchall()}
