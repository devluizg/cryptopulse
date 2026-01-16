"""
CryptoPulse - Configuração principal de testes.

Fixtures compartilhadas para todos os testes.
"""

import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

# Configurar para usar banco em memória nos testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# =============================================================================
# Event Loop
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria um event loop para toda a sessão de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Cria engine de teste com SQLite em memória."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Importar Base e criar tabelas
    from src.database.connection import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Cria sessão de banco para cada teste."""
    session_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with session_maker() as session:
        yield session
        await session.rollback()


# =============================================================================
# Model Fixtures
# =============================================================================

@pytest_asyncio.fixture
async def sample_asset(db_session: AsyncSession):
    """Cria um asset de teste."""
    from src.database.models import Asset
    
    asset = Asset(
        symbol="BTC",
        name="Bitcoin",
        coingecko_id="bitcoin",
        binance_symbol="BTCUSDT",
        is_active=True,
        priority=100,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset


@pytest_asyncio.fixture
async def sample_assets(db_session: AsyncSession):
    """Cria múltiplos assets de teste."""
    from src.database.models import Asset
    
    assets_data = [
        {"symbol": "BTC", "name": "Bitcoin", "coingecko_id": "bitcoin", "priority": 100},
        {"symbol": "ETH", "name": "Ethereum", "coingecko_id": "ethereum", "priority": 90},
        {"symbol": "SOL", "name": "Solana", "coingecko_id": "solana", "priority": 80},
    ]
    
    assets = []
    for data in assets_data:
        asset = Asset(**data, is_active=True)
        db_session.add(asset)
        assets.append(asset)
    
    await db_session.commit()
    for asset in assets:
        await db_session.refresh(asset)
    
    return assets


@pytest_asyncio.fixture
async def sample_score(db_session: AsyncSession, sample_asset):
    """Cria um score de teste."""
    from src.database.models import AssetScore
    
    score = AssetScore(
        asset_id=sample_asset.id,
        explosion_score=75.5,
        status="high",
        whale_accumulation_score=80.0,
        exchange_netflow_score=70.0,
        volume_anomaly_score=65.0,
        oi_pressure_score=75.0,
        narrative_momentum_score=85.0,
        price_usd=45000.0,
        price_change_24h=5.5,
        calculated_at=datetime.utcnow(),
    )
    db_session.add(score)
    await db_session.commit()
    await db_session.refresh(score)
    return score


@pytest_asyncio.fixture
async def sample_alert(db_session: AsyncSession, sample_asset):
    """Cria um alert de teste."""
    from src.database.models import Alert
    
    alert = Alert(
        asset_id=sample_asset.id,
        alert_type="score_high",
        severity="high",
        title="BTC entrou em zona de explosão",
        message="Bitcoin atingiu score 75.5",
        trigger_value=75.5,
        score_at_trigger=75.5,
        price_at_trigger=45000.0,
        is_read=False,
        created_at=datetime.utcnow(),
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)
    return alert


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_http_client():
    """Mock para cliente HTTP."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def mock_redis():
    """Mock para Redis."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    return redis


# =============================================================================
# Data Fixtures
# =============================================================================

@pytest.fixture
def whale_transaction_data():
    """Dados de transação de whale para testes."""
    return {
        "transactions": [
            {
                "hash": "0xabc123",
                "amount_usd": 5_000_000,
                "amount_crypto": 100.5,
                "transaction_type": "outflow",
                "from_exchange": True,
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "hash": "0xdef456",
                "amount_usd": 3_000_000,
                "amount_crypto": 60.2,
                "transaction_type": "inflow",
                "to_exchange": True,
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            },
        ],
        "historical_avg_volume": 4_000_000,
        "historical_avg_count": 3,
        "asset_symbol": "BTC",
    }


@pytest.fixture
def volume_data():
    """Dados de volume para testes."""
    return {
        "current_volume": 50_000_000_000,
        "avg_volume_7d": 30_000_000_000,
        "avg_volume_30d": 25_000_000_000,
        "volume_history": [25e9, 28e9, 30e9, 35e9, 40e9, 45e9, 50e9],
        "asset_symbol": "BTC",
    }


@pytest.fixture
def price_data_sample():
    """Dados de preço para testes."""
    return {
        "symbol": "BTC",
        "price_usd": 45000.0,
        "volume_24h": 30_000_000_000,
        "price_change_24h": 5.5,
        "high_24h": 46000.0,
        "low_24h": 43000.0,
        "timestamp": datetime.utcnow(),
        "source": "binance",
    }


@pytest.fixture
def score_calculation_data(whale_transaction_data, volume_data):
    """Dados completos para cálculo de score."""
    return {
        "asset_symbol": "BTC",
        "whale_data": whale_transaction_data,
        "netflow_data": {
            "net_flow": -5_000_000,
            "inflow": 10_000_000,
            "outflow": 15_000_000,
            "historical_avg_netflow": -2_000_000,
            "asset_symbol": "BTC",
        },
        "volume_data": volume_data,
        "oi_data": {
            "current_oi": 15_000_000_000,
            "oi_change_24h": 8.5,
            "historical_avg_oi": 12_000_000_000,
            "asset_symbol": "BTC",
        },
        "narrative_data": {
            "news_count": 15,
            "avg_sentiment": 0.7,
            "important_events": 2,
            "asset_symbol": "BTC",
        },
    }
