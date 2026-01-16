"""
CryptoPulse - Alembic Environment Configuration
Configuração para migrações async com SQLAlchemy
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Importar configurações do projeto
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.config.settings import settings
from src.database.connection import Base

# Importar TODOS os modelos para que o Alembic os detecte
from src.database.models.asset import Asset
from src.database.models.signal import AssetScore
from src.database.models.whale_transaction import WhaleTransaction
from src.database.models.exchange_flow import ExchangeFlow
from src.database.models.alert import Alert
from src.database.models.narrative_event import NarrativeEvent
from src.database.models.metric import MetricSnapshot
from src.database.models.price_data import PriceData

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dos modelos para autogenerate
target_metadata = Base.metadata

# ===========================================
# Database URL
# ===========================================

def get_url() -> str:
    """Retorna a URL do banco de dados"""
    return settings.database_url


# ===========================================
# Modo Offline (gera SQL sem conectar)
# ===========================================

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Gera o SQL sem precisar de conexão com o banco.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ===========================================
# Modo Online (conecta e executa)
# ===========================================

def do_run_migrations(connection: Connection) -> None:
    """Executa as migrações com uma conexão ativa"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode with async engine.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


# ===========================================
# Executar
# ===========================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
