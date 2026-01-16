"""
Testes para ThresholdMonitor.
"""

import pytest
from datetime import datetime, timedelta

from src.alerts.threshold_monitor import ThresholdMonitor, AlertCandidate
from src.alerts.templates import AlertType, AlertSeverity


class TestThresholdMonitor:
    """Testes para ThresholdMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Cria instância do monitor."""
        return ThresholdMonitor()
    
    @pytest.fixture
    def clean_monitor(self):
        """Cria monitor com cooldowns limpos."""
        monitor = ThresholdMonitor()
        monitor.clear_cooldowns()
        return monitor
    
    # ===========================================
    # Score Tests
    # ===========================================
    
    @pytest.mark.asyncio
    async def test_check_score_critical(self, clean_monitor):
        """Testa alerta de score crítico (>85)."""
        alerts = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=90.0,
        )
        
        # Pode gerar múltiplos alertas (critical + spike)
        critical_alerts = [a for a in alerts if a.alert_type == AlertType.SCORE_CRITICAL]
        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == AlertSeverity.CRITICAL
        assert critical_alerts[0].symbol == "BTC"
    
    @pytest.mark.asyncio
    async def test_check_score_high(self, clean_monitor):
        """Testa alerta de score alto (70-85)."""
        # Primeiro, definir um score anterior abaixo do threshold
        # Mas próximo o suficiente para não gerar SPIKE (delta < 15)
        clean_monitor._last_scores["BTC"] = 65.0
        
        alerts = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=75.0,  # Delta de 10, não gera spike
        )
        
        # Deve gerar apenas SCORE_HIGH (delta=10 < 15 para spike)
        high_alerts = [a for a in alerts if a.alert_type == AlertType.SCORE_HIGH]
        assert len(high_alerts) == 1
        assert high_alerts[0].severity == AlertSeverity.HIGH
    
    @pytest.mark.asyncio
    async def test_check_score_high_with_spike(self, clean_monitor):
        """Testa que score alto + spike gera dois alertas."""
        clean_monitor._last_scores["BTC"] = 55.0
        
        alerts = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=75.0,  # Delta de 20, gera spike também
        )
        
        # Deve gerar SCORE_HIGH e SCORE_SPIKE
        assert len(alerts) == 2
        alert_types = {a.alert_type for a in alerts}
        assert AlertType.SCORE_HIGH in alert_types
        assert AlertType.SCORE_SPIKE in alert_types
    
    @pytest.mark.asyncio
    async def test_check_score_no_alert_when_already_high(self, clean_monitor):
        """Testa que não gera alerta se já estava alto."""
        # Score anterior já alto
        clean_monitor._last_scores["BTC"] = 75.0
        
        alerts = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=78.0,
        )
        
        # Não deve gerar SCORE_HIGH pois não "entrou" na zona
        score_high_alerts = [a for a in alerts if a.alert_type == AlertType.SCORE_HIGH]
        assert len(score_high_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_check_score_spike(self, clean_monitor):
        """Testa alerta de spike de score."""
        clean_monitor._last_scores["BTC"] = 50.0
        
        alerts = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=70.0,  # +20 pontos
        )
        
        spike_alerts = [a for a in alerts if a.alert_type == AlertType.SCORE_SPIKE]
        assert len(spike_alerts) == 1
    
    @pytest.mark.asyncio
    async def test_check_score_drop(self, clean_monitor):
        """Testa alerta de queda de score."""
        clean_monitor._last_scores["BTC"] = 70.0
        
        alerts = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=50.0,  # -20 pontos
        )
        
        drop_alerts = [a for a in alerts if a.alert_type == AlertType.SCORE_DROP]
        assert len(drop_alerts) == 1
        assert drop_alerts[0].severity == AlertSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_check_score_no_alert_normal(self, clean_monitor):
        """Testa que não gera alerta para score normal."""
        clean_monitor._last_scores["BTC"] = 45.0
        
        alerts = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=48.0,  # Variação pequena
        )
        
        assert len(alerts) == 0
    
    @pytest.mark.asyncio
    async def test_check_score_cooldown(self, clean_monitor):
        """Testa que cooldown impede alertas duplicados."""
        # Primeiro alerta
        alerts1 = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=90.0,
        )
        critical_alerts1 = [a for a in alerts1 if a.alert_type == AlertType.SCORE_CRITICAL]
        assert len(critical_alerts1) == 1
        
        # Reset score para simular nova verificação
        clean_monitor._last_scores["BTC"] = 88.0
        
        # Segundo alerta (deveria estar em cooldown)
        alerts2 = await clean_monitor.check_score(
            asset_id=1,
            symbol="BTC",
            current_score=92.0,
        )
        
        critical_alerts2 = [a for a in alerts2 if a.alert_type == AlertType.SCORE_CRITICAL]
        assert len(critical_alerts2) == 0  # Cooldown ativo
    
    # ===========================================
    # Whale Transaction Tests
    # ===========================================
    
    @pytest.mark.asyncio
    async def test_check_whale_large_tx(self, clean_monitor):
        """Testa alerta de transação grande de whale."""
        alert = await clean_monitor.check_whale_transaction(
            asset_id=1,
            symbol="BTC",
            amount_usd=10_000_000,
            amount_crypto=220.5,
            tx_type="outflow",
        )
        
        assert alert is not None
        assert alert.alert_type == AlertType.WHALE_LARGE_TX
        assert "10" in alert.title or "M" in alert.title
    
    @pytest.mark.asyncio
    async def test_check_whale_small_tx_no_alert(self, clean_monitor):
        """Testa que transação pequena não gera alerta."""
        alert = await clean_monitor.check_whale_transaction(
            asset_id=1,
            symbol="BTC",
            amount_usd=1_000_000,  # Abaixo do threshold
            amount_crypto=22.0,
            tx_type="outflow",
        )
        
        assert alert is None
    
    @pytest.mark.asyncio
    async def test_check_whale_severity_by_amount(self, clean_monitor):
        """Testa severidade baseada no valor da transação."""
        # $50M+ = CRITICAL
        alert_critical = await clean_monitor.check_whale_transaction(
            asset_id=1,
            symbol="BTC",
            amount_usd=60_000_000,
            amount_crypto=1200.0,
            tx_type="outflow",
        )
        assert alert_critical.severity == AlertSeverity.CRITICAL
        
        # Limpar cooldown
        clean_monitor.clear_cooldowns()
        
        # $20-50M = HIGH
        alert_high = await clean_monitor.check_whale_transaction(
            asset_id=1,
            symbol="BTC",
            amount_usd=30_000_000,
            amount_crypto=600.0,
            tx_type="outflow",
        )
        assert alert_high.severity == AlertSeverity.HIGH
        
        # Limpar cooldown
        clean_monitor.clear_cooldowns()
        
        # $5-10M = LOW
        alert_low = await clean_monitor.check_whale_transaction(
            asset_id=1,
            symbol="BTC",
            amount_usd=7_000_000,
            amount_crypto=140.0,
            tx_type="outflow",
        )
        assert alert_low.severity == AlertSeverity.LOW
    
    # ===========================================
    # Price Change Tests
    # ===========================================
    
    @pytest.mark.asyncio
    async def test_check_price_surge(self, clean_monitor):
        """Testa alerta de alta de preço."""
        alert = await clean_monitor.check_price_change(
            asset_id=1,
            symbol="BTC",
            change_percent=15.0,
            current_price=50000.0,
        )
        
        assert alert is not None
        assert alert.alert_type == AlertType.PRICE_SURGE
        assert "15" in alert.message or "subiu" in alert.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_price_dump(self, clean_monitor):
        """Testa alerta de queda de preço."""
        alert = await clean_monitor.check_price_change(
            asset_id=1,
            symbol="BTC",
            change_percent=-12.0,
            current_price=40000.0,
        )
        
        assert alert is not None
        assert alert.alert_type == AlertType.PRICE_DUMP
        assert "12" in alert.message or "caiu" in alert.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_price_normal_no_alert(self, clean_monitor):
        """Testa que variação normal não gera alerta."""
        alert = await clean_monitor.check_price_change(
            asset_id=1,
            symbol="BTC",
            change_percent=5.0,  # Normal
            current_price=45000.0,
        )
        
        assert alert is None
    
    # ===========================================
    # Volume Spike Tests
    # ===========================================
    
    @pytest.mark.asyncio
    async def test_check_volume_spike(self, clean_monitor):
        """Testa alerta de pico de volume."""
        alert = await clean_monitor.check_volume_spike(
            asset_id=1,
            symbol="BTC",
            current_volume=100_000_000_000,
            avg_volume=25_000_000_000,  # 4x
        )
        
        assert alert is not None
        assert alert.alert_type == AlertType.VOLUME_SPIKE
        assert alert.data["multiplier"] == pytest.approx(4.0)
    
    @pytest.mark.asyncio
    async def test_check_volume_normal_no_alert(self, clean_monitor):
        """Testa que volume normal não gera alerta."""
        alert = await clean_monitor.check_volume_spike(
            asset_id=1,
            symbol="BTC",
            current_volume=50_000_000_000,
            avg_volume=30_000_000_000,  # 1.67x (abaixo de 3x)
        )
        
        assert alert is None
    
    @pytest.mark.asyncio
    async def test_check_volume_zero_avg(self, clean_monitor):
        """Testa com média de volume zero."""
        alert = await clean_monitor.check_volume_spike(
            asset_id=1,
            symbol="BTC",
            current_volume=50_000_000_000,
            avg_volume=0,
        )
        
        assert alert is None
    
    # ===========================================
    # Utility Tests
    # ===========================================
    
    def test_get_cooldown_key(self, monitor):
        """Testa geração de chave de cooldown."""
        key = monitor._get_cooldown_key(AlertType.SCORE_HIGH, "BTC")
        
        assert "score_high" in key
        assert "BTC" in key
    
    def test_clear_cooldowns(self, monitor):
        """Testa limpeza de cooldowns."""
        monitor._cooldowns["test"] = datetime.utcnow()
        assert len(monitor._cooldowns) > 0
        
        monitor.clear_cooldowns()
        
        assert len(monitor._cooldowns) == 0
    
    def test_get_stats(self, monitor):
        """Testa obtenção de estatísticas."""
        stats = monitor.get_stats()
        
        assert "check_count" in stats
        assert "alert_count" in stats
        assert "active_cooldowns" in stats
        assert "tracked_symbols" in stats
    
    def test_get_top_factors(self, monitor):
        """Testa obtenção de principais fatores."""
        indicator_scores = {
            "whale_accumulation": 90.0,
            "exchange_netflow": 70.0,
            "volume_anomaly": 50.0,
        }
        
        factors = monitor._get_top_factors(indicator_scores)
        
        assert "Whales" in factors
        assert "90" in factors
    
    def test_get_top_factors_empty(self, monitor):
        """Testa com scores vazios."""
        factors = monitor._get_top_factors({})
        
        assert "insuficientes" in factors.lower()


class TestAlertCandidate:
    """Testes para AlertCandidate."""
    
    def test_create_candidate(self):
        """Testa criação de candidato a alerta."""
        candidate = AlertCandidate(
            alert_type=AlertType.SCORE_HIGH,
            severity=AlertSeverity.HIGH,
            title="Test Alert",
            message="Test Message",
            asset_id=1,
            symbol="BTC",
            data={"score": 75.0},
        )
        
        assert candidate.alert_type == AlertType.SCORE_HIGH
        assert candidate.severity == AlertSeverity.HIGH
        assert candidate.symbol == "BTC"
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        candidate = AlertCandidate(
            alert_type=AlertType.WHALE_LARGE_TX,
            severity=AlertSeverity.MEDIUM,
            title="Whale Alert",
            message="Large transaction detected",
            asset_id=1,
            symbol="ETH",
            data={"amount_usd": 10_000_000},
        )
        
        result = candidate.to_dict()
        
        assert result["alert_type"] == "whale_large_tx"
        assert result["severity"] == "medium"
        assert result["symbol"] == "ETH"
        assert result["data"]["amount_usd"] == 10_000_000
