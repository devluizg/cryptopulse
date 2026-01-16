"""
Testes de integração para repositórios.

NOTA: Estes testes requerem PostgreSQL rodando.
Para executar: pytest tests/integration/database/ -v --run-integration
"""

import pytest
from datetime import datetime, timedelta

# Marcar todos os testes deste módulo como integração
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skip(reason="Requer PostgreSQL - execute com docker-compose up")
]


class TestAssetRepository:
    """Testes de integração para AssetRepository."""
    
    @pytest.mark.asyncio
    async def test_create_asset(self, db_session):
        """Testa criação de asset."""
        from src.database.models import Asset
        from src.database.repositories import AssetRepository
        
        repo = AssetRepository(db_session)
        
        asset = await repo.create(
            symbol="TEST",
            name="Test Coin",
            coingecko_id="test-coin",
            is_active=True,
            priority=50,
        )
        
        assert asset.id is not None
        assert asset.symbol == "TEST"


class TestScoreRepository:
    """Testes de integração para ScoreRepository."""
    
    @pytest.mark.asyncio
    async def test_create_score(self, db_session, sample_asset):
        """Testa criação de score."""
        from src.database.repositories import ScoreRepository
        
        repo = ScoreRepository(db_session)
        
        score = await repo.create_score(
            asset_id=sample_asset.id,
            explosion_score=75.5,
            status="high",
        )
        
        assert score.id is not None


class TestAlertRepository:
    """Testes de integração para AlertRepository."""
    
    @pytest.mark.asyncio
    async def test_create_alert(self, db_session, sample_asset):
        """Testa criação de alerta."""
        from src.database.repositories import AlertRepository
        
        repo = AlertRepository(db_session)
        
        alert = await repo.create_alert(
            asset_id=sample_asset.id,
            alert_type="score_high",
            severity="high",
            title="Test Alert",
            message="Test message",
        )
        
        assert alert.id is not None
