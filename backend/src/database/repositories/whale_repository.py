"""
CryptoPulse - Whale Transaction Repository
Operações de banco para transações de baleias
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import WhaleTransaction, Asset
from src.database.repositories.base_repository import BaseRepository


class WhaleRepository(BaseRepository[WhaleTransaction]):
    """Repositório para operações com WhaleTransaction."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(WhaleTransaction, session)
    
    # ===========================================
    # Buscar transações
    # ===========================================
    
    async def get_recent(
        self, 
        hours: int = 24, 
        limit: int = 100
    ) -> List[WhaleTransaction]:
        """Retorna transações recentes."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(WhaleTransaction)
            .where(WhaleTransaction.timestamp >= since)
            .order_by(desc(WhaleTransaction.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_asset(
        self, 
        asset_id: int, 
        hours: int = 24,
        limit: int = 50
    ) -> List[WhaleTransaction]:
        """Retorna transações de um ativo."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(WhaleTransaction)
            .where(
                and_(
                    WhaleTransaction.asset_id == asset_id,
                    WhaleTransaction.timestamp >= since
                )
            )
            .order_by(desc(WhaleTransaction.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_symbol(
        self, 
        symbol: str, 
        hours: int = 24
    ) -> List[WhaleTransaction]:
        """Retorna transações pelo símbolo."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(WhaleTransaction)
            .join(Asset)
            .where(
                and_(
                    Asset.symbol == symbol.upper(),
                    WhaleTransaction.timestamp >= since
                )
            )
            .order_by(desc(WhaleTransaction.timestamp))
        )
        return list(result.scalars().all())
    
    async def get_by_type(
        self, 
        transaction_type: str,
        hours: int = 24
    ) -> List[WhaleTransaction]:
        """Retorna transações por tipo."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(WhaleTransaction)
            .where(
                and_(
                    WhaleTransaction.transaction_type == transaction_type,
                    WhaleTransaction.timestamp >= since
                )
            )
            .order_by(desc(WhaleTransaction.timestamp))
        )
        return list(result.scalars().all())
    
    async def get_large_transactions(
        self, 
        min_usd: float = 10_000_000,
        hours: int = 24
    ) -> List[WhaleTransaction]:
        """Retorna transações acima de um valor."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(WhaleTransaction)
            .where(
                and_(
                    WhaleTransaction.amount_usd >= min_usd,
                    WhaleTransaction.timestamp >= since
                )
            )
            .order_by(desc(WhaleTransaction.amount_usd))
        )
        return list(result.scalars().all())
    
    async def get_by_tx_hash(self, tx_hash: str) -> Optional[WhaleTransaction]:
        """Busca transação por hash."""
        result = await self.session.execute(
            select(WhaleTransaction)
            .where(WhaleTransaction.tx_hash == tx_hash)
        )
        return result.scalar_one_or_none()
    
    # ===========================================
    # Estatísticas
    # ===========================================
    
    async def get_total_volume(
        self, 
        asset_id: int, 
        hours: int = 24
    ) -> float:
        """Retorna volume total de whale em USD."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(func.sum(WhaleTransaction.amount_usd))
            .where(
                and_(
                    WhaleTransaction.asset_id == asset_id,
                    WhaleTransaction.timestamp >= since
                )
            )
        )
        return result.scalar() or 0.0
    
    async def get_netflow(
        self, 
        asset_id: int, 
        hours: int = 24
    ) -> dict:
        """Calcula netflow de whale (exchange_deposit - exchange_withdrawal)."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Inflow (depósitos em exchange)
        inflow_result = await self.session.execute(
            select(func.sum(WhaleTransaction.amount_usd))
            .where(
                and_(
                    WhaleTransaction.asset_id == asset_id,
                    WhaleTransaction.timestamp >= since,
                    WhaleTransaction.transaction_type == "exchange_deposit"
                )
            )
        )
        inflow = inflow_result.scalar() or 0.0
        
        # Outflow (saques de exchange)
        outflow_result = await self.session.execute(
            select(func.sum(WhaleTransaction.amount_usd))
            .where(
                and_(
                    WhaleTransaction.asset_id == asset_id,
                    WhaleTransaction.timestamp >= since,
                    WhaleTransaction.transaction_type == "exchange_withdrawal"
                )
            )
        )
        outflow = outflow_result.scalar() or 0.0
        
        return {
            "inflow": inflow,
            "outflow": outflow,
            "netflow": inflow - outflow
        }
    
    async def count_by_asset(
        self, 
        asset_id: int, 
        hours: int = 24
    ) -> int:
        """Conta transações de um ativo."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(func.count(WhaleTransaction.id))
            .where(
                and_(
                    WhaleTransaction.asset_id == asset_id,
                    WhaleTransaction.timestamp >= since
                )
            )
        )
        return result.scalar() or 0
    
    async def get_stats_by_asset(
        self, 
        asset_id: int, 
        hours: int = 24
    ) -> dict:
        """Retorna estatísticas completas de whale para um ativo."""
        count = await self.count_by_asset(asset_id, hours)
        volume = await self.get_total_volume(asset_id, hours)
        netflow = await self.get_netflow(asset_id, hours)
        
        return {
            "count": count,
            "total_volume_usd": volume,
            **netflow
        }
    
    # ===========================================
    # Criação
    # ===========================================
    
    async def create_transaction(
        self,
        asset_id: int,
        amount: float,
        amount_usd: float,
        transaction_type: str,
        timestamp: datetime,
        tx_hash: Optional[str] = None,
        from_address: Optional[str] = None,
        from_owner: Optional[str] = None,
        to_address: Optional[str] = None,
        to_owner: Optional[str] = None,
        blockchain: Optional[str] = None,
        raw_data: Optional[dict] = None
    ) -> WhaleTransaction:
        """Cria uma nova transação de whale."""
        return await self.create(
            asset_id=asset_id,
            amount=amount,
            amount_usd=amount_usd,
            transaction_type=transaction_type,
            timestamp=timestamp,
            tx_hash=tx_hash,
            from_address=from_address,
            from_owner=from_owner,
            to_address=to_address,
            to_owner=to_owner,
            blockchain=blockchain,
            raw_data=raw_data
        )
    
    async def tx_exists(self, tx_hash: str) -> bool:
        """Verifica se transação já existe pelo hash."""
        tx = await self.get_by_tx_hash(tx_hash)
        return tx is not None
