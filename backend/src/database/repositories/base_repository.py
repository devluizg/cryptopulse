"""
CryptoPulse - Base Repository
Classe base com operações CRUD genéricas
"""

from typing import TypeVar, Generic, Type, List, Optional, Any, cast
from sqlalchemy import select, update, delete, func, CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import Base

# Tipo genérico para os modelos
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repositório base com operações CRUD.
    
    Uso:
        class AssetRepository(BaseRepository[Asset]):
            def __init__(self, session: AsyncSession):
                super().__init__(Asset, session)
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    # ===========================================
    # CREATE
    # ===========================================
    
    async def create(self, **kwargs: Any) -> ModelType:
        """Cria um novo registro."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def create_many(self, items: List[dict]) -> List[ModelType]:
        """Cria múltiplos registros."""
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        return instances
    
    # ===========================================
    # READ
    # ===========================================
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Busca por ID."""
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, 'id') == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """Retorna todos os registros com paginação."""
        query = select(self.model)
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_field(
        self, 
        field: str, 
        value: Any
    ) -> Optional[ModelType]:
        """Busca por um campo específico."""
        column = getattr(self.model, field)
        result = await self.session.execute(
            select(self.model).where(column == value)
        )
        return result.scalar_one_or_none()
    
    async def get_many_by_field(
        self, 
        field: str, 
        value: Any,
        limit: int = 100
    ) -> List[ModelType]:
        """Busca múltiplos por um campo."""
        column = getattr(self.model, field)
        result = await self.session.execute(
            select(self.model).where(column == value).limit(limit)
        )
        return list(result.scalars().all())
    
    async def exists(self, id: int) -> bool:
        """Verifica se registro existe."""
        result = await self.session.execute(
            select(func.count()).select_from(self.model).where(
                getattr(self.model, 'id') == id
            )
        )
        count = result.scalar()
        return count is not None and count > 0
    
    async def count(self) -> int:
        """Conta total de registros."""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
    
    # ===========================================
    # UPDATE
    # ===========================================
    
    async def update(self, id: int, **kwargs: Any) -> Optional[ModelType]:
        """Atualiza um registro por ID."""
        await self.session.execute(
            update(self.model)
            .where(getattr(self.model, 'id') == id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(id)
    
    async def update_instance(self, instance: ModelType, **kwargs: Any) -> ModelType:
        """Atualiza uma instância existente."""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    # ===========================================
    # DELETE
    # ===========================================
    
    async def delete(self, id: int) -> bool:
        """Deleta por ID."""
        result = await self.session.execute(
            delete(self.model).where(getattr(self.model, 'id') == id)
        )
        await self.session.flush()
        return cast(int, result.rowcount) > 0
    
    async def delete_many(self, ids: List[int]) -> int:
        """Deleta múltiplos por IDs."""
        result = await self.session.execute(
            delete(self.model).where(getattr(self.model, 'id').in_(ids))
        )
        await self.session.flush()
        return cast(int, result.rowcount)
