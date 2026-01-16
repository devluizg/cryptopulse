"""
Testes de integração para endpoints da API.

NOTA: Estes testes requerem a aplicação rodando.
Para executar: pytest tests/integration/api/ -v --run-integration
"""

import pytest

# Marcar todos os testes deste módulo como integração
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skip(reason="Requer aplicação rodando - execute com docker-compose up")
]


class TestHealthEndpoint:
    """Testes para endpoint de health check."""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Testa endpoint /health."""
        pass


class TestAssetsEndpoint:
    """Testes para endpoints de assets."""
    
    @pytest.mark.asyncio
    async def test_list_assets(self):
        """Testa listagem de assets."""
        pass


class TestSignalsEndpoint:
    """Testes para endpoints de signals/scores."""
    
    @pytest.mark.asyncio
    async def test_list_signals(self):
        """Testa listagem de sinais."""
        pass


class TestAlertsEndpoint:
    """Testes para endpoints de alertas."""
    
    @pytest.mark.asyncio
    async def test_list_alerts(self):
        """Testa listagem de alertas."""
        pass
