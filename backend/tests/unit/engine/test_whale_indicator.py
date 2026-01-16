"""
Testes para WhaleIndicator.
"""

import pytest
from datetime import datetime, timedelta

from src.engine.indicators.whale_indicator import WhaleIndicator


class TestWhaleIndicator:
    """Testes para WhaleIndicator."""
    
    @pytest.fixture
    def indicator(self):
        """Cria instância do indicador."""
        return WhaleIndicator(weight=0.25)
    
    @pytest.mark.asyncio
    async def test_calculate_no_transactions(self, indicator):
        """Testa cálculo sem transações - score neutro."""
        data = {
            "transactions": [],
            "historical_avg_volume": 1_000_000,
            "historical_avg_count": 5,
            "asset_symbol": "BTC",
        }
        
        result = await indicator.calculate_with_details(data)
        
        assert result["score"] == 50.0
        assert result["details"]["transaction_count"] == 0
        assert result["details"]["net_direction"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_calculate_accumulation(self, indicator):
        """Testa detecção de acumulação (bullish)."""
        now = datetime.utcnow()
        data = {
            "transactions": [
                {
                    "amount_usd": 10_000_000,
                    "transaction_type": "outflow",
                    "from_exchange": True,
                    "timestamp": now.isoformat(),
                },
                {
                    "amount_usd": 5_000_000,
                    "transaction_type": "outflow",
                    "from_exchange": True,
                    "timestamp": (now - timedelta(hours=1)).isoformat(),
                },
            ],
            "historical_avg_volume": 5_000_000,
            "historical_avg_count": 2,
            "asset_symbol": "BTC",
        }
        
        result = await indicator.calculate_with_details(data)
        
        assert result["score"] > 50.0  # Acumulação = bullish
        assert result["details"]["net_direction"] == "accumulation"
        assert result["details"]["transaction_count"] == 2
    
    @pytest.mark.asyncio
    async def test_calculate_distribution(self, indicator):
        """Testa detecção de distribuição (bearish)."""
        now = datetime.utcnow()
        data = {
            "transactions": [
                {
                    "amount_usd": 10_000_000,
                    "transaction_type": "inflow",
                    "to_exchange": True,
                    "timestamp": now.isoformat(),
                },
                {
                    "amount_usd": 8_000_000,
                    "transaction_type": "inflow",
                    "to_exchange": True,
                    "timestamp": (now - timedelta(hours=1)).isoformat(),
                },
            ],
            "historical_avg_volume": 5_000_000,
            "historical_avg_count": 2,
            "asset_symbol": "BTC",
        }
        
        result = await indicator.calculate_with_details(data)
        
        # Distribuição = mais inflow que outflow = bearish
        assert result["details"]["net_direction"] == "distribution"
    
    @pytest.mark.asyncio
    async def test_calculate_high_volume(self, indicator):
        """Testa score alto para volume muito acima da média."""
        now = datetime.utcnow()
        data = {
            "transactions": [
                {
                    "amount_usd": 50_000_000,
                    "transaction_type": "outflow",
                    "from_exchange": True,
                    "timestamp": now.isoformat(),
                },
            ],
            "historical_avg_volume": 5_000_000,  # 10x abaixo do atual
            "historical_avg_count": 1,
            "asset_symbol": "BTC",
        }
        
        result = await indicator.calculate_with_details(data)
        
        assert result["score"] > 60.0
        assert result["details"]["sub_scores"]["volume_score"] > 60.0
    
    @pytest.mark.asyncio
    async def test_calculate_low_volume(self, indicator):
        """Testa score baixo para volume abaixo da média."""
        now = datetime.utcnow()
        data = {
            "transactions": [
                {
                    "amount_usd": 1_000_000,
                    "transaction_type": "outflow",
                    "from_exchange": True,
                    "timestamp": now.isoformat(),
                },
            ],
            "historical_avg_volume": 10_000_000,  # 10x acima do atual
            "historical_avg_count": 5,
            "asset_symbol": "BTC",
        }
        
        result = await indicator.calculate_with_details(data)
        
        assert result["details"]["sub_scores"]["volume_score"] < 50.0
    
    @pytest.mark.asyncio
    async def test_calculate_recency_recent_transactions(self, indicator):
        """Testa que transações recentes têm maior peso."""
        now = datetime.utcnow()
        data = {
            "transactions": [
                {
                    "amount_usd": 5_000_000,
                    "transaction_type": "outflow",
                    "from_exchange": True,
                    "timestamp": now.isoformat(),  # Agora
                },
            ],
            "historical_avg_volume": 5_000_000,
            "historical_avg_count": 1,
            "asset_symbol": "BTC",
        }
        
        result = await indicator.calculate_with_details(data)
        
        # Transação muito recente = recency score alto
        assert result["details"]["sub_scores"]["recency_score"] > 70.0
    
    @pytest.mark.asyncio
    async def test_calculate_recency_old_transactions(self, indicator):
        """Testa que transações antigas têm menor peso."""
        old_time = datetime.utcnow() - timedelta(hours=20)
        data = {
            "transactions": [
                {
                    "amount_usd": 5_000_000,
                    "transaction_type": "outflow",
                    "from_exchange": True,
                    "timestamp": old_time.isoformat(),  # 20h atrás
                },
            ],
            "historical_avg_volume": 5_000_000,
            "historical_avg_count": 1,
            "asset_symbol": "BTC",
        }
        
        result = await indicator.calculate_with_details(data)
        
        # Transação antiga = recency score baixo
        assert result["details"]["sub_scores"]["recency_score"] < 50.0
    
    @pytest.mark.asyncio
    async def test_calculate_without_historical_data(self, indicator):
        """Testa cálculo sem dados históricos."""
        now = datetime.utcnow()
        data = {
            "transactions": [
                {
                    "amount_usd": 5_000_000,
                    "transaction_type": "outflow",
                    "from_exchange": True,
                    "timestamp": now.isoformat(),
                },
            ],
            "historical_avg_volume": 0,  # Sem histórico
            "historical_avg_count": 0,
            "asset_symbol": "BTC",
        }
        
        result = await indicator.calculate_with_details(data)
        
        # Deve retornar score válido mesmo sem histórico
        assert 0 <= result["score"] <= 100
    
    @pytest.mark.asyncio
    async def test_calculate_simple(self, indicator):
        """Testa método calculate simples (sem detalhes)."""
        data = {
            "transactions": [],
            "historical_avg_volume": 1_000_000,
            "historical_avg_count": 5,
            "asset_symbol": "BTC",
        }
        
        score = await indicator.calculate(data)
        
        assert score == 50.0
        assert isinstance(score, float)
    
    def test_ratio_to_score_average(self, indicator):
        """Testa conversão de ratio 1.0 (na média)."""
        score = indicator._ratio_to_score(1.0)
        
        assert score == pytest.approx(50.0, abs=0.1)
    
    def test_ratio_to_score_double(self, indicator):
        """Testa conversão de ratio 2.0 (2x a média)."""
        score = indicator._ratio_to_score(2.0)
        
        assert score > 60.0
    
    def test_ratio_to_score_half(self, indicator):
        """Testa conversão de ratio 0.5 (metade da média)."""
        score = indicator._ratio_to_score(0.5)
        
        assert score < 40.0
    
    def test_ratio_to_score_zero(self, indicator):
        """Testa conversão de ratio 0."""
        score = indicator._ratio_to_score(0)
        
        assert score == 30.0
    
    def test_generate_reason_accumulation(self, indicator):
        """Testa geração de razão para acumulação."""
        reason = indicator._generate_reason("accumulation", 75.0, 5)
        
        assert "acumulando" in reason.lower()
        assert "acima da média" in reason.lower()
    
    def test_generate_reason_distribution(self, indicator):
        """Testa geração de razão para distribuição."""
        reason = indicator._generate_reason("distribution", 35.0, 3)
        
        assert "distribuindo" in reason.lower()
        assert "abaixo da média" in reason.lower()
    
    def test_indicator_weight(self, indicator):
        """Testa que o peso está configurado corretamente."""
        assert indicator.weight == 0.25
        assert indicator.name == "whale_accumulation"
