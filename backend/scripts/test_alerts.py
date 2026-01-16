#!/usr/bin/env python3
"""
Teste do sistema de alertas do CryptoPulse.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Configurar logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO",
)


async def test_templates():
    """Testa templates de alertas."""
    from src.alerts import AlertType, AlertSeverity, ALERT_TEMPLATES
    
    print("\n" + "=" * 60)
    print("📝 Testando Templates de Alertas")
    print("=" * 60)
    
    print(f"\n✅ Total de templates: {len(ALERT_TEMPLATES)}")
    
    for alert_type, template in ALERT_TEMPLATES.items():
        print(f"   - {alert_type.value}: {template.default_severity.value}")
    
    # Testa formatação
    template = ALERT_TEMPLATES[AlertType.SCORE_HIGH]
    title = template.format_title(symbol="BTC")
    message = template.format_message(
        symbol="BTC",
        score=75.5,
        factors="Whales (85), Volume (72)",
    )
    
    print(f"\n📌 Exemplo de formatação:")
    print(f"   Título: {title}")
    print(f"   Mensagem: {message[:80]}...")
    
    return True


async def test_threshold_monitor():
    """Testa o monitor de thresholds."""
    from src.alerts import AlertType, AlertSeverity, ThresholdMonitor
    
    print("\n" + "=" * 60)
    print("🔍 Testando ThresholdMonitor")
    print("=" * 60)
    
    monitor = ThresholdMonitor()
    
    # Teste 1: Score normal (não deve alertar)
    print("\n📊 Teste 1: Score normal (50)")
    alerts = await monitor.check_score(
        asset_id=1,
        symbol="BTC",
        current_score=50.0,
    )
    print(f"   Alertas gerados: {len(alerts)}")
    assert len(alerts) == 0, "Não deveria gerar alerta para score 50"
    print("   ✅ Passou")
    
    # Teste 2: Score alto (deve alertar quando ENTRA na zona)
    # Primeiro registra um score baixo, depois sobe para zona alta
    print("\n📊 Teste 2: Score alto (entrando na zona 75)")
    monitor._last_scores["ETH"] = 65.0  # Score anterior abaixo de 70
    alerts = await monitor.check_score(
        asset_id=1,
        symbol="ETH",
        current_score=75.0,  # Agora entra na zona alta
        indicator_scores={
            "whale_accumulation": 80.0,
            "exchange_netflow": 70.0,
            "volume_anomaly": 75.0,
            "oi_pressure": 65.0,
            "narrative_momentum": 60.0,
        },
    )
    print(f"   Alertas gerados: {len(alerts)}")
    if alerts:
        print(f"   Tipo: {alerts[0].alert_type.value}")
        print(f"   Título: {alerts[0].title}")
    assert len(alerts) == 1, "Deveria gerar 1 alerta ao entrar na zona alta"
    assert alerts[0].alert_type == AlertType.SCORE_HIGH
    print("   ✅ Passou")
    
    # Teste 3: Score crítico
    print("\n📊 Teste 3: Score crítico (90)")
    monitor._last_scores["SOL"] = 80.0  # Score anterior abaixo de 85
    alerts = await monitor.check_score(
        asset_id=1,
        symbol="SOL",
        current_score=90.0,
    )
    print(f"   Alertas gerados: {len(alerts)}")
    if alerts:
        print(f"   Severidade: {alerts[0].severity.value}")
    assert len(alerts) == 1, "Deveria gerar 1 alerta crítico"
    assert alerts[0].severity == AlertSeverity.CRITICAL
    print("   ✅ Passou")
    
    # Teste 4: Cooldown (não deve alertar de novo)
    print("\n📊 Teste 4: Cooldown (mesmo ativo)")
    alerts = await monitor.check_score(
        asset_id=1,
        symbol="SOL",
        current_score=92.0,
    )
    print(f"   Alertas gerados: {len(alerts)} (esperado: 0 por cooldown)")
    assert len(alerts) == 0, "Não deveria alertar - está em cooldown"
    print("   ✅ Passou")
    
    # Teste 5: Score spike
    print("\n📊 Teste 5: Score spike (+20 pontos)")
    monitor._last_scores["ADA"] = 45.0
    alerts = await monitor.check_score(
        asset_id=4,
        symbol="ADA",
        current_score=65.0,  # +20 pontos
    )
    print(f"   Alertas gerados: {len(alerts)}")
    if alerts:
        print(f"   Tipo: {alerts[0].alert_type.value}")
    assert len(alerts) == 1, "Deveria gerar alerta de spike"
    assert alerts[0].alert_type == AlertType.SCORE_SPIKE
    print("   ✅ Passou")
    
    # Teste 6: Score drop
    print("\n📊 Teste 6: Score drop (-18 pontos)")
    monitor._last_scores["DOGE"] = 60.0
    alerts = await monitor.check_score(
        asset_id=5,
        symbol="DOGE",
        current_score=42.0,  # -18 pontos
    )
    print(f"   Alertas gerados: {len(alerts)}")
    if alerts:
        print(f"   Tipo: {alerts[0].alert_type.value}")
    assert len(alerts) == 1, "Deveria gerar alerta de drop"
    assert alerts[0].alert_type == AlertType.SCORE_DROP
    print("   ✅ Passou")
    
    # Teste 7: Score já na zona alta (não deve alertar se já estava lá)
    print("\n📊 Teste 7: Score já na zona alta (não deve alertar)")
    monitor._last_scores["LINK"] = 72.0  # Já estava na zona alta
    alerts = await monitor.check_score(
        asset_id=6,
        symbol="LINK",
        current_score=75.0,  # Continua na zona alta
    )
    print(f"   Alertas gerados: {len(alerts)} (esperado: 0 - já estava na zona)")
    assert len(alerts) == 0, "Não deveria alertar - já estava na zona alta"
    print("   ✅ Passou")
    
    print(f"\n📈 Stats do monitor: {monitor.get_stats()}")
    
    return True


async def test_whale_alerts():
    """Testa alertas de whale."""
    from src.alerts import AlertType, AlertSeverity, ThresholdMonitor
    
    print("\n" + "=" * 60)
    print("🐋 Testando Alertas de Whale")
    print("=" * 60)
    
    monitor = ThresholdMonitor()
    
    # Teste 1: Transação pequena (não alerta)
    print("\n📊 Teste 1: Transação pequena ($1M)")
    alert = await monitor.check_whale_transaction(
        asset_id=1,
        symbol="BTC",
        amount_usd=1_000_000,
        amount_crypto=10.5,
        tx_type="transfer",
    )
    print(f"   Alerta gerado: {alert is not None}")
    assert alert is None, "Não deveria alertar para $1M"
    print("   ✅ Passou")
    
    # Teste 2: Transação grande ($10M)
    print("\n📊 Teste 2: Transação grande ($10M)")
    alert = await monitor.check_whale_transaction(
        asset_id=1,
        symbol="BTC",
        amount_usd=10_000_000,
        amount_crypto=105.5,
        tx_type="transfer",
    )
    print(f"   Alerta gerado: {alert is not None}")
    if alert:
        print(f"   Título: {alert.title}")
        print(f"   Severidade: {alert.severity.value}")
    assert alert is not None, "Deveria alertar para $10M"
    assert alert.severity == AlertSeverity.MEDIUM
    print("   ✅ Passou")
    
    # Teste 3: Transação muito grande ($50M)
    print("\n📊 Teste 3: Transação muito grande ($50M)")
    alert = await monitor.check_whale_transaction(
        asset_id=2,
        symbol="ETH",
        amount_usd=50_000_000,
        amount_crypto=15000.0,
        tx_type="exchange_deposit",
    )
    print(f"   Alerta gerado: {alert is not None}")
    if alert:
        print(f"   Severidade: {alert.severity.value}")
    assert alert is not None, "Deveria alertar para $50M"
    assert alert.severity == AlertSeverity.CRITICAL
    print("   ✅ Passou")
    
    return True


async def test_price_alerts():
    """Testa alertas de preço."""
    from src.alerts import AlertType, AlertSeverity, ThresholdMonitor
    
    print("\n" + "=" * 60)
    print("💰 Testando Alertas de Preço")
    print("=" * 60)
    
    monitor = ThresholdMonitor()
    
    # Teste 1: Mudança pequena (não alerta)
    print("\n📊 Teste 1: Mudança pequena (+5%)")
    alert = await monitor.check_price_change(
        asset_id=1,
        symbol="BTC",
        change_percent=5.0,
        current_price=45000.0,
    )
    print(f"   Alerta gerado: {alert is not None}")
    assert alert is None, "Não deveria alertar para +5%"
    print("   ✅ Passou")
    
    # Teste 2: Surge (+15%)
    print("\n📊 Teste 2: Price surge (+15%)")
    alert = await monitor.check_price_change(
        asset_id=1,
        symbol="BTC",
        change_percent=15.0,
        current_price=51750.0,
    )
    print(f"   Alerta gerado: {alert is not None}")
    if alert:
        print(f"   Tipo: {alert.alert_type.value}")
        print(f"   Título: {alert.title}")
    assert alert is not None, "Deveria alertar para +15%"
    assert alert.alert_type == AlertType.PRICE_SURGE
    print("   ✅ Passou")
    
    # Teste 3: Dump (-12%)
    print("\n📊 Teste 3: Price dump (-12%)")
    alert = await monitor.check_price_change(
        asset_id=2,
        symbol="ETH",
        change_percent=-12.0,
        current_price=2640.0,
    )
    print(f"   Alerta gerado: {alert is not None}")
    if alert:
        print(f"   Tipo: {alert.alert_type.value}")
    assert alert is not None, "Deveria alertar para -12%"
    assert alert.alert_type == AlertType.PRICE_DUMP
    print("   ✅ Passou")
    
    return True


async def test_volume_alerts():
    """Testa alertas de volume."""
    from src.alerts import AlertType, AlertSeverity, ThresholdMonitor
    
    print("\n" + "=" * 60)
    print("📊 Testando Alertas de Volume")
    print("=" * 60)
    
    monitor = ThresholdMonitor()
    
    # Teste 1: Volume normal (não alerta)
    print("\n📊 Teste 1: Volume normal (1.5x)")
    alert = await monitor.check_volume_spike(
        asset_id=1,
        symbol="BTC",
        current_volume=150_000_000,
        avg_volume=100_000_000,
    )
    print(f"   Alerta gerado: {alert is not None}")
    assert alert is None, "Não deveria alertar para 1.5x"
    print("   ✅ Passou")
    
    # Teste 2: Volume spike (5x)
    print("\n📊 Teste 2: Volume spike (5x)")
    alert = await monitor.check_volume_spike(
        asset_id=1,
        symbol="BTC",
        current_volume=500_000_000,
        avg_volume=100_000_000,
    )
    print(f"   Alerta gerado: {alert is not None}")
    if alert:
        print(f"   Título: {alert.title}")
    assert alert is not None, "Deveria alertar para 5x"
    print("   ✅ Passou")
    
    return True


async def test_alert_manager_stats():
    """Testa estatísticas do AlertManager."""
    from src.alerts import AlertManager
    
    print("\n" + "=" * 60)
    print("📈 Testando AlertManager Stats")
    print("=" * 60)
    
    manager = AlertManager()
    stats = manager.get_stats()
    
    print(f"\n📊 Stats do AlertManager:")
    print(f"   Process count: {stats['process_count']}")
    print(f"   Created alerts: {stats['created_alerts']}")
    print(f"   Sent notifications: {stats['sent_notifications']}")
    print(f"\n📡 Canais:")
    for channel_name, channel_stats in stats['channels'].items():
        print(f"   - {channel_name}: enabled={channel_stats['enabled']}")
    
    return True


async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🧪 CryptoPulse - Teste do Sistema de Alertas")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Templates", test_templates),
        ("ThresholdMonitor", test_threshold_monitor),
        ("Whale Alerts", test_whale_alerts),
        ("Price Alerts", test_price_alerts),
        ("Volume Alerts", test_volume_alerts),
        ("AlertManager Stats", test_alert_manager_stats),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"\n✅ {test_name}: PASSOU")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FALHOU")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name}: ERRO - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"   ✅ Passou: {passed}")
    print(f"   ❌ Falhou: {failed}")
    print(f"   📝 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️ {failed} teste(s) falharam")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
