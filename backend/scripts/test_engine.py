#!/usr/bin/env python3
"""
Script de teste para o Scoring Engine.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Adicionar backend ao path (não src)
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.engine import ScoreCalculator
from src.engine.indicators import (
    WhaleIndicator,
    VolumeIndicator,
    OpenInterestIndicator,
    NarrativeIndicator,
    NetflowIndicator,
)


async def test_whale_indicator():
    """Testa WhaleIndicator."""
    print("\n" + "=" * 60)
    print("🐋 Testando WhaleIndicator")
    print("=" * 60)
    
    indicator = WhaleIndicator(weight=0.25)
    
    data_bullish = {
        "transactions": [
            {"amount_usd": 5_000_000, "transaction_type": "outflow", "timestamp": datetime.utcnow()},
            {"amount_usd": 3_000_000, "transaction_type": "outflow", "timestamp": datetime.utcnow()},
            {"amount_usd": 2_000_000, "transaction_type": "inflow", "timestamp": datetime.utcnow()},
        ],
        "historical_avg_volume": 5_000_000,
        "historical_avg_count": 2,
        "asset_symbol": "BTC",
    }
    
    result = await indicator.calculate_with_details(data_bullish)
    print(f"\n📊 Cenário Bullish (acumulação):")
    print(f"   Score: {result['score']:.1f}")
    print(f"   Direção: {result['details']['net_direction']}")
    print(f"   Razão: {result['details']['reason']}")
    
    data_neutral = {
        "transactions": [],
        "historical_avg_volume": 5_000_000,
        "historical_avg_count": 2,
        "asset_symbol": "ETH",
    }
    
    result = await indicator.calculate_with_details(data_neutral)
    print(f"\n📊 Cenário Neutro (sem atividade):")
    print(f"   Score: {result['score']:.1f}")
    print(f"   Razão: {result['details']['reason']}")
    
    print("\n✅ WhaleIndicator OK")


async def test_volume_indicator():
    """Testa VolumeIndicator."""
    print("\n" + "=" * 60)
    print("📈 Testando VolumeIndicator")
    print("=" * 60)
    
    indicator = VolumeIndicator(weight=0.20)
    
    data = {
        "current_volume": 500_000_000,
        "historical_volumes": [100_000_000, 120_000_000, 110_000_000, 105_000_000, 115_000_000] * 4,
        "price_change_percent": 5.0,
        "asset_symbol": "BTC",
    }
    
    result = await indicator.calculate_with_details(data)
    print(f"\n📊 Cenário: Volume 5x a média")
    print(f"   Score: {result['score']:.1f}")
    print(f"   Z-Score: {result['details']['z_score']:.2f}")
    print(f"   Volume vs Média: {result['details']['volume_vs_avg']:.1f}x")
    print(f"   Anomalia: {result['details']['anomaly_detected']}")
    print(f"   Razão: {result['details']['reason']}")
    
    print("\n✅ VolumeIndicator OK")


async def test_oi_indicator():
    """Testa OpenInterestIndicator."""
    print("\n" + "=" * 60)
    print("📊 Testando OpenInterestIndicator")
    print("=" * 60)
    
    indicator = OpenInterestIndicator(weight=0.15)
    
    data = {
        "current_oi": 1_500_000_000,
        "previous_oi": 1_200_000_000,
        "price_change_percent": -3.0,
        "funding_rate": -0.0005,
        "long_short_ratio": 0.85,
        "asset_symbol": "BTC",
    }
    
    result = await indicator.calculate_with_details(data)
    print(f"\n📊 Cenário: Short Squeeze Setup")
    print(f"   Score: {result['score']:.1f}")
    print(f"   OI Change: {result['details']['oi_change_percent']:.1f}%")
    print(f"   Funding Rate: {result['details']['funding_rate']:.4f}")
    print(f"   Interpretação: {result['details']['interpretation']}")
    print(f"   Razão: {result['details']['reason']}")
    
    print("\n✅ OpenInterestIndicator OK")


async def test_narrative_indicator():
    """Testa NarrativeIndicator."""
    print("\n" + "=" * 60)
    print("📰 Testando NarrativeIndicator")
    print("=" * 60)
    
    indicator = NarrativeIndicator(weight=0.15)
    
    data = {
        "news": [
            {"title": "Bitcoin ETF approved by SEC", "sentiment": "bullish", "published_at": datetime.utcnow()},
            {"title": "Major bank announces BTC partnership", "sentiment": "bullish", "published_at": datetime.utcnow()},
            {"title": "BTC price analysis", "sentiment": "neutral", "published_at": datetime.utcnow()},
        ],
        "mention_count": 150,
        "historical_mention_avg": 50,
        "events": [
            {"type": "etf", "title": "ETF Approval"},
        ],
        "asset_symbol": "BTC",
    }
    
    result = await indicator.calculate_with_details(data)
    print(f"\n📊 Cenário: Notícias Muito Positivas")
    print(f"   Score: {result['score']:.1f}")
    print(f"   News Count: {result['details']['news_count']}")
    print(f"   Avg Sentiment: {result['details']['avg_sentiment']}")
    print(f"   Overall Sentiment: {result['details']['overall_sentiment']}")
    print(f"   Razão: {result['details']['reason']}")
    
    print("\n✅ NarrativeIndicator OK")


async def test_netflow_indicator():
    """Testa NetflowIndicator."""
    print("\n" + "=" * 60)
    print("🔄 Testando NetflowIndicator")
    print("=" * 60)
    
    indicator = NetflowIndicator(weight=0.25)
    
    data = {
        "inflow_usd": 50_000_000,
        "outflow_usd": 150_000_000,
        "historical_netflows": [-50_000_000, -30_000_000, -80_000_000, -40_000_000],
        "asset_symbol": "BTC",
    }
    
    result = await indicator.calculate_with_details(data)
    print(f"\n📊 Cenário: Forte Saída de Exchanges")
    print(f"   Score: {result['score']:.1f}")
    print(f"   Netflow: ${result['details']['netflow_usd']:,.0f}")
    print(f"   Ratio: {result['details']['netflow_ratio']:.2%}")
    print(f"   Interpretação: {result['details']['interpretation']}")
    print(f"   Razão: {result['details']['reason']}")
    
    print("\n✅ NetflowIndicator OK")


async def test_score_calculator():
    """Testa o ScoreCalculator completo."""
    print("\n" + "=" * 60)
    print("🎯 Testando ScoreCalculator (Score Final)")
    print("=" * 60)
    
    calculator = ScoreCalculator()
    
    data = {
        "asset_symbol": "BTC",
        "whale_data": {
            "transactions": [
                {"amount_usd": 10_000_000, "transaction_type": "outflow", "timestamp": datetime.utcnow()},
                {"amount_usd": 5_000_000, "transaction_type": "outflow", "timestamp": datetime.utcnow()},
            ],
            "historical_avg_volume": 5_000_000,
            "historical_avg_count": 1,
        },
        "netflow_data": {
            "inflow_usd": 30_000_000,
            "outflow_usd": 100_000_000,
            "historical_netflows": [-20_000_000, -30_000_000],
        },
        "volume_data": {
            "current_volume": 300_000_000,
            "historical_volumes": [100_000_000] * 20,
            "price_change_percent": 4.0,
        },
        "oi_data": {
            "current_oi": 1_500_000_000,
            "previous_oi": 1_200_000_000,
            "price_change_percent": 4.0,
            "funding_rate": -0.0003,
            "long_short_ratio": 0.9,
        },
        "narrative_data": {
            "news": [
                {"title": "BTC breaks resistance", "sentiment": "bullish", "published_at": datetime.utcnow()},
            ],
            "mention_count": 80,
            "historical_mention_avg": 40,
        },
    }
    
    result = await calculator.calculate(data)
    
    print(f"\n🎯 Resultado Final:")
    print(f"   Explosion Score: {result['explosion_score']:.1f}")
    print(f"   Status: {result['status'].upper()}")
    print(f"\n📊 Scores por Indicador:")
    for name, score in result['indicator_scores'].items():
        print(f"   - {name}: {score:.1f}")
    print(f"\n📝 Resumo: {result['summary']}")
    
    if result['explosion_score'] >= 70:
        print("\n🔴 ALERTA: Score em zona de EXPLOSÃO!")
    elif result['explosion_score'] >= 40:
        print("\n🟡 Score em zona de ATENÇÃO")
    else:
        print("\n🟢 Score em zona NORMAL")
    
    print("\n✅ ScoreCalculator OK")


async def test_scenario_bearish():
    """Testa cenário bearish."""
    print("\n" + "=" * 60)
    print("📉 Testando Cenário BEARISH")
    print("=" * 60)
    
    calculator = ScoreCalculator()
    
    data = {
        "asset_symbol": "ETH",
        "whale_data": {
            "transactions": [
                {"amount_usd": 8_000_000, "transaction_type": "inflow", "timestamp": datetime.utcnow()},
                {"amount_usd": 5_000_000, "transaction_type": "inflow", "timestamp": datetime.utcnow()},
            ],
            "historical_avg_volume": 3_000_000,
            "historical_avg_count": 1,
        },
        "netflow_data": {
            "inflow_usd": 80_000_000,
            "outflow_usd": 20_000_000,
            "historical_netflows": [30_000_000, 40_000_000],
        },
        "volume_data": {
            "current_volume": 50_000_000,
            "historical_volumes": [100_000_000] * 20,
            "price_change_percent": -5.0,
        },
        "oi_data": {
            "current_oi": 800_000_000,
            "previous_oi": 1_000_000_000,
            "price_change_percent": -5.0,
            "funding_rate": 0.001,
            "long_short_ratio": 1.5,
        },
        "narrative_data": {
            "news": [
                {"title": "ETH faces regulatory concerns", "sentiment": "bearish", "published_at": datetime.utcnow()},
            ],
            "mention_count": 20,
            "historical_mention_avg": 40,
        },
    }
    
    result = await calculator.calculate(data)
    
    print(f"\n🎯 Resultado Bearish:")
    print(f"   Explosion Score: {result['explosion_score']:.1f}")
    print(f"   Status: {result['status'].upper()}")
    print(f"\n📊 Scores por Indicador:")
    for name, score in result['indicator_scores'].items():
        print(f"   - {name}: {score:.1f}")
    
    print("\n✅ Cenário Bearish OK")


async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🧪 CryptoPulse - Teste do Scoring Engine")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        await test_whale_indicator()
        await test_volume_indicator()
        await test_oi_indicator()
        await test_narrative_indicator()
        await test_netflow_indicator()
        await test_score_calculator()
        await test_scenario_bearish()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
