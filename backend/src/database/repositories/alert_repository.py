"""
CryptoPulse - Alert Repository
Operações de banco para alertas
"""

from typing import List, Optional, cast
from datetime import datetime, timedelta
from sqlalchemy import select, update, desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Alert, Asset
from src.database.repositories.base_repository import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """Repositório para operações com Alert."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Alert, session)
    
    # ===========================================
    # Buscas
    # ===========================================
    
    async def get_recent(
        self, 
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Alert]:
        """Retorna alertas recentes."""
        query = select(Alert)
        
        if unread_only:
            query = query.where(Alert.is_read == False)
        
        query = query.order_by(desc(Alert.created_at)).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_asset(
        self, 
        asset_id: int, 
        limit: int = 20
    ) -> List[Alert]:
        """Retorna alertas de um ativo específico."""
        result = await self.session.execute(
            select(Alert)
            .where(Alert.asset_id == asset_id)
            .order_by(desc(Alert.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_symbol(
        self, 
        symbol: str, 
        limit: int = 20
    ) -> List[Alert]:
        """Retorna alertas pelo símbolo do ativo."""
        result = await self.session.execute(
            select(Alert)
            .join(Asset)
            .where(Asset.symbol == symbol.upper())
            .order_by(desc(Alert.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_severity(
        self, 
        severity: str, 
        limit: int = 50
    ) -> List[Alert]:
        """Retorna alertas por severidade."""
        result = await self.session.execute(
            select(Alert)
            .where(Alert.severity == severity)
            .order_by(desc(Alert.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_type(
        self, 
        alert_type: str, 
        limit: int = 50
    ) -> List[Alert]:
        """Retorna alertas por tipo."""
        result = await self.session.execute(
            select(Alert)
            .where(Alert.alert_type == alert_type)
            .order_by(desc(Alert.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_critical_unread(self) -> List[Alert]:
        """Retorna alertas críticos não lidos."""
        result = await self.session.execute(
            select(Alert)
            .where(
                and_(
                    Alert.severity == "critical",
                    Alert.is_read == False
                )
            )
            .order_by(desc(Alert.created_at))
        )
        return list(result.scalars().all())
    
    # ===========================================
    # Ações
    # ===========================================
    
    async def mark_as_read(self, alert_id: int) -> bool:
        """Marca alerta como lido."""
        result = await self.session.execute(
            update(Alert)
            .where(Alert.id == alert_id)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.session.flush()
        return cast(int, result.rowcount) > 0
    
    async def mark_many_as_read(self, alert_ids: List[int]) -> int:
        """Marca múltiplos alertas como lidos."""
        result = await self.session.execute(
            update(Alert)
            .where(Alert.id.in_(alert_ids))
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.session.flush()
        return cast(int, result.rowcount)
    
    async def mark_all_as_read(self) -> int:
        """Marca todos alertas como lidos."""
        result = await self.session.execute(
            update(Alert)
            .where(Alert.is_read == False)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.session.flush()
        return cast(int, result.rowcount)
    
    async def dismiss(self, alert_id: int) -> bool:
        """Dispensa um alerta."""
        result = await self.session.execute(
            update(Alert)
            .where(Alert.id == alert_id)
            .values(is_dismissed=True)
        )
        await self.session.flush()
        return cast(int, result.rowcount) > 0
    
    # ===========================================
    # Estatísticas
    # ===========================================
    
    async def count_unread(self) -> int:
        """Conta alertas não lidos."""
        result = await self.session.execute(
            select(func.count(Alert.id))
            .where(Alert.is_read == False)
        )
        return result.scalar() or 0
    
    async def count_by_severity(self) -> dict:
        """Conta alertas por severidade."""
        result = await self.session.execute(
            select(Alert.severity, func.count(Alert.id))
            .group_by(Alert.severity)
        )
        return {row[0]: row[1] for row in result.fetchall()}
    
    async def count_today(self) -> int:
        """Conta alertas de hoje."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.count(Alert.id))
            .where(Alert.created_at >= today)
        )
        return result.scalar() or 0
    
    # ===========================================
    # Criação
    # ===========================================
    
    async def create_alert(
        self,
        asset_id: int,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        trigger_value: Optional[float] = None,
        trigger_reason: Optional[dict] = None,
        score_at_trigger: Optional[float] = None,
        price_at_trigger: Optional[float] = None
    ) -> Alert:
        """Cria um novo alerta."""
        return await self.create(
            asset_id=asset_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            trigger_value=trigger_value,
            trigger_reason=trigger_reason,
            score_at_trigger=score_at_trigger,
            price_at_trigger=price_at_trigger
        )
    
    # ===========================================
    # Limpeza
    # ===========================================
    
    async def delete_old(self, days: int = 30) -> int:
        """Deleta alertas antigos."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(Alert.id).where(Alert.created_at < cutoff)
        )
        ids = [row[0] for row in result.fetchall()]
        
        if ids:
            return await self.delete_many(ids)
        return 0

    async def get_unread(self, limit: int = 50) -> List[Alert]:
        """Retorna alertas não lidos."""
        return await self.get_recent(limit=limit, unread_only=True)
