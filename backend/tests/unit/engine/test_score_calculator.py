"""
Testes para ScoreCalculator.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.engine.score_calculator import ScoreCalculator


class TestScoreCalculator:
    """Testes para ScoreCalculator."""
    
    @pytest.fixture
    def calculator(self):
        """Cria instância do calculador."""
        return ScoreCalculator()
    
    @pytest.fixture
    def calculator_custom_weights(self):
        """Cria calculador com pesos customizados."""
        weights = {
            "whale_accumulation": 0.4,
            "exchange_netflow": 0.3,
            "volume_anomaly": 0.15,
            "oi_pressure": 0.1,
            "narrative_momentum": 0.05,
        }
        return ScoreCalculator(custom_weights=weights)
    
    def test_init_default_weights(self, calculator):
        """Testa inicialização com pesos padrão."""
        assert calculator.indicators["whale"].weight == 0.25
        assert calculator.indicators["netflow"].weight == 0.25
        assert calculator.indicators["volume"].weight == 0.20
        assert calculator.indicators["oi"].weight == 0.15
        assert calculator.indicators["narrative"].weight == 0.15
    
    def test_init_custom_weights(self, calculator_custom_weights):
        """Testa inicialização com pesos customizados."""
        assert calculator_custom_weights.indicators["whale"].weight == 0.4
        assert calculator_custom_weights.indicators["netflow"].weight == 0.3
    
    @pytest.mark.asyncio
    async def test_calculate_all_neutral(self, calculator):
        """Testa cálculo quando todos indicadores são neutros."""
        # Mock todos os indicadores para retornar 50
        for name, indicator in calculator.indicators.items():
            indicator.calculate_with_details = AsyncMock(
                return_value={"score": 50.0, "details": {}}
            )
        
        data = {
            "asset_symbol": "BTC",
            "whale_data": {},
            "netflow_data": {},
            "volume_data": {},
            "oi_data": {},
            "narrative_data": {},
        }
        
        result = await calculator.calculate(data)
        
        assert result["explosion_score"] == 50.0
        # Score de 50 está na zona de atenção (40-70)
        assert result["status"] == "attention"
        assert result["asset_symbol"] == "BTC"
    
    @pytest.mark.asyncio
    async def test_calculate_low_score(self, calculator):
        """Testa cálculo com score baixo (zona low)."""
        # Mock todos os indicadores para retornar valores baixos
        for indicator in calculator.indicators.values():
            indicator.calculate_with_details = AsyncMock(
                return_value={"score": 30.0, "details": {}}
            )
        
        data = {
            "asset_symbol": "BTC",
            "whale_data": {},
            "netflow_data": {},
            "volume_data": {},
            "oi_data": {},
            "narrative_data": {},
        }
        
        result = await calculator.calculate(data)
        
        assert result["explosion_score"] == 30.0
        assert result["status"] == "low"
    
    @pytest.mark.asyncio
    async def test_calculate_high_score(self, calculator):
        """Testa cálculo com score alto."""
        # Mock todos os indicadores para retornar valores altos
        for indicator in calculator.indicators.values():
            indicator.calculate_with_details = AsyncMock(
                return_value={"score": 85.0, "details": {}}
            )
        
        data = {
            "asset_symbol": "BTC",
            "whale_data": {},
            "netflow_data": {},
            "volume_data": {},
            "oi_data": {},
            "narrative_data": {},
        }
        
        result = await calculator.calculate(data)
        
        assert result["explosion_score"] >= 70.0
        assert result["status"] == "high"
    
    @pytest.mark.asyncio
    async def test_calculate_attention_score(self, calculator):
        """Testa cálculo com score de atenção."""
        # Mock para score de atenção (40-70)
        for indicator in calculator.indicators.values():
            indicator.calculate_with_details = AsyncMock(
                return_value={"score": 55.0, "details": {}}
            )
        
        data = {
            "asset_symbol": "ETH",
            "whale_data": {},
            "netflow_data": {},
            "volume_data": {},
            "oi_data": {},
            "narrative_data": {},
        }
        
        result = await calculator.calculate(data)
        
        assert 40.0 <= result["explosion_score"] < 70.0
        assert result["status"] == "attention"
    
    @pytest.mark.asyncio
    async def test_calculate_with_indicator_error(self, calculator):
        """Testa cálculo quando um indicador falha."""
        # Whale indicator falha
        calculator.indicators["whale"].calculate_with_details = AsyncMock(
            side_effect=Exception("API Error")
        )
        # Outros retornam normal
        for name, indicator in calculator.indicators.items():
            if name != "whale":
                indicator.calculate_with_details = AsyncMock(
                    return_value={"score": 60.0, "details": {}}
                )
        
        data = {
            "asset_symbol": "BTC",
            "whale_data": {},
            "netflow_data": {},
            "volume_data": {},
            "oi_data": {},
            "narrative_data": {},
        }
        
        result = await calculator.calculate(data)
        
        # Deve usar valor default (50) para whale e continuar
        assert result["indicator_scores"]["whale_accumulation"] == 50.0
        assert "error" in result["indicator_details"]["whale_accumulation"]
    
    @pytest.mark.asyncio
    async def test_calculate_quick(self, calculator):
        """Testa método calculate_quick."""
        for indicator in calculator.indicators.values():
            indicator.calculate_with_details = AsyncMock(
                return_value={"score": 65.0, "details": {}}
            )
        
        data = {"asset_symbol": "BTC"}
        
        score = await calculator.calculate_quick(data)
        
        assert isinstance(score, float)
        assert score == 65.0
    
    @pytest.mark.asyncio
    async def test_calculate_returns_all_fields(self, calculator):
        """Testa que calculate retorna todos os campos esperados."""
        for indicator in calculator.indicators.values():
            indicator.calculate_with_details = AsyncMock(
                return_value={"score": 50.0, "details": {"test": "data"}}
            )
        
        data = {"asset_symbol": "BTC"}
        
        result = await calculator.calculate(data)
        
        assert "explosion_score" in result
        assert "status" in result
        assert "indicator_scores" in result
        assert "indicator_details" in result
        assert "weights" in result
        assert "summary" in result
        assert "calculated_at" in result
        assert "asset_symbol" in result
    
    @pytest.mark.asyncio
    async def test_calculate_score_clamped(self, calculator):
        """Testa que score é clampado entre 0 e 100."""
        # Mock para retornar valor muito alto
        for indicator in calculator.indicators.values():
            indicator.calculate_with_details = AsyncMock(
                return_value={"score": 150.0, "details": {}}
            )
        
        data = {"asset_symbol": "BTC"}
        
        result = await calculator.calculate(data)
        
        assert result["explosion_score"] <= 100.0
    
    def test_determine_status_high(self, calculator):
        """Testa determinação de status alto."""
        assert calculator._determine_status(85.0) == "high"
        assert calculator._determine_status(70.0) == "high"
    
    def test_determine_status_attention(self, calculator):
        """Testa determinação de status de atenção."""
        assert calculator._determine_status(55.0) == "attention"
        assert calculator._determine_status(40.0) == "attention"
        assert calculator._determine_status(50.0) == "attention"
    
    def test_determine_status_low(self, calculator):
        """Testa determinação de status baixo."""
        assert calculator._determine_status(30.0) == "low"
        assert calculator._determine_status(0.0) == "low"
        assert calculator._determine_status(39.9) == "low"
    
    def test_generate_summary_high(self, calculator):
        """Testa geração de resumo para score alto."""
        summary = calculator._generate_summary(
            score=85.0,
            indicator_scores={
                "whale_accumulation": 90.0,
                "exchange_netflow": 80.0,
                "volume_anomaly": 70.0,
            },
            status="high",
        )
        
        assert "ALERTA" in summary or "explosão" in summary.lower()
    
    def test_generate_summary_attention(self, calculator):
        """Testa geração de resumo para score de atenção."""
        summary = calculator._generate_summary(
            score=55.0,
            indicator_scores={
                "whale_accumulation": 60.0,
                "exchange_netflow": 50.0,
            },
            status="attention",
        )
        
        assert "atenção" in summary.lower()
    
    def test_generate_summary_low(self, calculator):
        """Testa geração de resumo para score baixo."""
        summary = calculator._generate_summary(
            score=30.0,
            indicator_scores={
                "whale_accumulation": 30.0,
                "exchange_netflow": 25.0,
            },
            status="low",
        )
        
        assert "normal" in summary.lower()
    
    def test_indicator_name_mapping(self, calculator):
        """Testa mapeamento de nomes de indicadores."""
        assert calculator._indicator_name("whale_accumulation") == "Whales"
        assert calculator._indicator_name("exchange_netflow") == "Netflow"
        assert calculator._indicator_name("volume_anomaly") == "Volume"
        assert calculator._indicator_name("unknown") == "unknown"
    
    def test_get_indicator_status(self, calculator):
        """Testa obtenção de status dos indicadores."""
        status = calculator.get_indicator_status()
        
        assert "whale" in status
        assert "netflow" in status
        assert "volume" in status
        assert "oi" in status
        assert "narrative" in status
    
    def test_update_weights(self, calculator):
        """Testa atualização de pesos."""
        calculator.update_weights({
            "whale": 0.5,
            "volume_anomaly": 0.1,
        })
        
        assert calculator.indicators["whale"].weight == 0.5
        assert calculator.indicators["volume"].weight == 0.1
