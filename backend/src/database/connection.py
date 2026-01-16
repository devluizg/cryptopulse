"""
CryptoPulse - Database Connection
Configuração da conexão async com PostgreSQL usando SQLAlchemy 2.0
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from src.config.settings import settings


# ===========================================
# Base para todos os modelos
# ===========================================

class Base(DeclarativeBase):
    """
    Classe base para todos os modelos SQLAlchemy.
    Todos os modelos devem herdar desta classe.
    """
    pass


# ===========================================
# Engine e Session
# ===========================================

# Engine async para PostgreSQL
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries em modo debug
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_recycle=1800,  # Recicla conexões a cada 30 min
    pool_pre_ping=True,  # Verifica conexão antes de usar
)

# Fábrica de sessões async
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ===========================================
# Dependency Injection para FastAPI
# ===========================================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que fornece uma sessão de banco de dados.
    Uso no FastAPI:
    
    @app.get("/items")
    async def get_items(session: AsyncSession = Depends(get_session)):
        ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ===========================================
# Funções de inicialização
# ===========================================

async def init_db() -> None:
    """
    Inicializa o banco de dados.
    Cria todas as tabelas se não existirem.
    
    NOTA: Em produção, use Alembic para migrações.
    Esta função é útil apenas para desenvolvimento/testes.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Fecha conexões do banco de dados.
    Deve ser chamado ao encerrar a aplicação.
    """
    await engine.dispose()
