"""
Testes para BaseIndicator.
"""

import pytest
import numpy as np
from unittest.mock import AsyncMock

from src.engine.indicators.base_indicator import BaseIndicator


class ConcreteIndicator(BaseIndicator):
    """Implementação concreta para testes."""
    
    async def calculate(self, data):
        return 50.0
    
    async def calculate_with_details(self, data):
        return {"score": 50.0, "details": {}}


class TestBaseIndicator:
    """Testes para a classe BaseIndicator."""
    
    def test_init_default_weight(self):
        """Testa inicialização com peso padrão."""
        indicator = ConcreteIndicator(name="test")
        
        assert indicator.name == "test"
        assert indicator.weight == 1.0
    
    def test_init_custom_weight(self):
        """Testa inicialização com peso customizado."""
        indicator = ConcreteIndicator(name="test", weight=0.25)
        
        assert indicator.weight == 0.25
    
    def test_weight_clamped_min(self):
        """Testa que peso negativo é ajustado para 0."""
        indicator = ConcreteIndicator(name="test", weight=-0.5)
        
        assert indicator.weight == 0.0
    
    def test_weight_clamped_max(self):
        """Testa que peso > 1 é ajustado para 1."""
        indicator = ConcreteIndicator(name="test", weight=1.5)
        
        assert indicator.weight == 1.0
    
    def test_normalize_score_middle(self):
        """Testa normalização de valor no meio do range."""
        indicator = ConcreteIndicator(name="test")
        
        result = indicator.normalize_score(50, min_val=0, max_val=100)
        
        assert result == 50.0
    
    def test_normalize_score_min(self):
        """Testa normalização do valor mínimo."""
        indicator = ConcreteIndicator(name="test")
        
        result = indicator.normalize_score(0, min_val=0, max_val=100)
        
        assert result == 0.0
    
    def test_normalize_score_max(self):
        """Testa normalização do valor máximo."""
        indicator = ConcreteIndicator(name="test")
        
        result = indicator.normalize_score(100, min_val=0, max_val=100)
        
        assert result == 100.0
    
    def test_normalize_score_above_max(self):
        """Testa que valor acima do máximo é clampado."""
        indicator = ConcreteIndicator(name="test")
        
        result = indicator.normalize_score(150, min_val=0, max_val=100)
        
        assert result == 100.0
    
    def test_normalize_score_below_min(self):
        """Testa que valor abaixo do mínimo é clampado."""
        indicator = ConcreteIndicator(name="test")
        
        result = indicator.normalize_score(-50, min_val=0, max_val=100)
        
        assert result == 0.0
    
    def test_normalize_score_equal_min_max(self):
        """Testa normalização quando min == max."""
        indicator = ConcreteIndicator(name="test")
        
        result = indicator.normalize_score(50, min_val=50, max_val=50)
        
        assert result == 50.0
    
    def test_clamp_score_within_range(self):
        """Testa clamp de valor dentro do range."""
        indicator = ConcreteIndicator(name="test")
        
        assert indicator.clamp_score(50.0) == 50.0
        assert indicator.clamp_score(0.0) == 0.0
        assert indicator.clamp_score(100.0) == 100.0
    
    def test_clamp_score_above(self):
        """Testa clamp de valor acima de 100."""
        indicator = ConcreteIndicator(name="test")
        
        assert indicator.clamp_score(150.0) == 100.0
    
    def test_clamp_score_below(self):
        """Testa clamp de valor abaixo de 0."""
        indicator = ConcreteIndicator(name="test")
        
        assert indicator.clamp_score(-20.0) == 0.0
    
    def test_calculate_z_score_normal(self):
        """Testa cálculo de z-score com dados normais."""
        indicator = ConcreteIndicator(name="test")
        values = [10, 20, 30, 40, 50]
        
        # Média = 30, std ≈ 14.14
        z_score = indicator.calculate_z_score(30, values)
        
        assert z_score == pytest.approx(0.0, abs=0.01)
    
    def test_calculate_z_score_above_mean(self):
        """Testa z-score para valor acima da média."""
        indicator = ConcreteIndicator(name="test")
        values = [10, 20, 30, 40, 50]
        
        z_score = indicator.calculate_z_score(50, values)
        
        assert z_score > 1.0
    
    def test_calculate_z_score_below_mean(self):
        """Testa z-score para valor abaixo da média."""
        indicator = ConcreteIndicator(name="test")
        values = [10, 20, 30, 40, 50]
        
        z_score = indicator.calculate_z_score(10, values)
        
        assert z_score < -1.0
    
    def test_calculate_z_score_empty_list(self):
        """Testa z-score com lista vazia."""
        indicator = ConcreteIndicator(name="test")
        
        z_score = indicator.calculate_z_score(50, [])
        
        assert z_score == 0.0
    
    def test_calculate_z_score_single_value(self):
        """Testa z-score com apenas um valor."""
        indicator = ConcreteIndicator(name="test")
        
        z_score = indicator.calculate_z_score(50, [50])
        
        assert z_score == 0.0
    
    def test_calculate_z_score_zero_std(self):
        """Testa z-score quando todos valores são iguais (std=0)."""
        indicator = ConcreteIndicator(name="test")
        
        z_score = indicator.calculate_z_score(50, [50, 50, 50, 50])
        
        assert z_score == 0.0
    
    def test_z_score_to_percentile_zero(self):
        """Testa conversão de z-score 0 para percentil 50."""
        indicator = ConcreteIndicator(name="test")
        
        percentile = indicator.z_score_to_percentile(0)
        
        assert percentile == pytest.approx(50.0, abs=0.1)
    
    def test_z_score_to_percentile_positive(self):
        """Testa conversão de z-score positivo."""
        indicator = ConcreteIndicator(name="test")
        
        percentile = indicator.z_score_to_percentile(2.0)
        
        assert percentile > 50.0
        assert percentile < 100.0
    
    def test_z_score_to_percentile_negative(self):
        """Testa conversão de z-score negativo."""
        indicator = ConcreteIndicator(name="test")
        
        percentile = indicator.z_score_to_percentile(-2.0)
        
        assert percentile < 50.0
        assert percentile > 0.0
    
    def test_weighted_average_simple(self):
        """Testa média ponderada simples."""
        indicator = ConcreteIndicator(name="test")
        
        result = indicator.weighted_average([100, 50], [1, 1])
        
        assert result == 75.0
    
    def test_weighted_average_with_weights(self):
        """Testa média ponderada com pesos diferentes."""
        indicator = ConcreteIndicator(name="test")
        
        # 100*0.8 + 50*0.2 = 80 + 10 = 90
        result = indicator.weighted_average([100, 50], [0.8, 0.2])
        
        assert result == 90.0
    
    def test_weighted_average_empty(self):
        """Testa média ponderada com listas vazias."""
        indicator = ConcreteIndicator(name="test")
        
        result = indicator.weighted_average([], [])
        
        assert result == 0.0
    
    def test_exponential_decay_weights(self):
        """Testa geração de pesos com decaimento exponencial."""
        indicator = ConcreteIndicator(name="test")
        
        weights = indicator.exponential_decay_weights(5, decay=0.9)
        
        assert len(weights) == 5
        # Mais recente deve ter maior peso
        assert weights[-1] > weights[0]
    
    def test_exponential_decay_weights_empty(self):
        """Testa geração de pesos com count 0."""
        indicator = ConcreteIndicator(name="test")
        
        weights = indicator.exponential_decay_weights(0)
        
        assert weights == []
    
    def test_get_status_initial(self):
        """Testa status inicial do indicador."""
        indicator = ConcreteIndicator(name="test", weight=0.25)
        
        status = indicator.get_status()
        
        assert status["name"] == "test"
        assert status["weight"] == 0.25
        assert status["last_score"] is None
        assert status["last_calculation"] is None
    
    def test_update_state(self):
        """Testa atualização de estado interno."""
        indicator = ConcreteIndicator(name="test")
        
        indicator._update_state(
            score=75.0,
            raw_data={"test": "data"},
            details={"detail": "value"},
        )
        
        status = indicator.get_status()
        assert status["last_score"] == 75.0
        assert status["last_calculation"] is not None
        assert status["last_details"] == {"detail": "value"}
    
    def test_repr(self):
        """Testa representação string do indicador."""
        indicator = ConcreteIndicator(name="test", weight=0.25)
        
        repr_str = repr(indicator)
        
        assert "ConcreteIndicator" in repr_str
        assert "test" in repr_str
        assert "0.25" in repr_str
