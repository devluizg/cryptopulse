#!/usr/bin/env python3
"""
Script de teste para os coletores de dados.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from loguru import logger

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>", level="INFO")


async def test_price_collector(symbol: str = "BTC") -> bool:
    print("\n" + "=" * 60)
    print("📈 Testando Price Collector")
    print("=" * 60)
    
    from src.collectors import PriceCollector
    
    collector = PriceCollector()
    
    try:
        health = await collector.health_check()
        print(f"\n🏥 Health Check: {health['status']}")
        
        print(f"\n📊 Coletando preço de {symbol}...")
        price = await collector.collect_single(symbol)
        
        if price:
            print(f"   ✅ {symbol}: ${price.price_usd:,.2f}")
            print(f"      Volume 24h: ${price.volume_24h:,.0f}")
            print(f"      Variação 24h: {price.price_change_24h or 0:.2f}%")
            print(f"      Fonte: {price.source}")
        else:
            print(f"   ❌ Não foi possível coletar preço de {symbol}")
        
        print("\n📊 Coletando preços de múltiplos ativos...")
        prices = await collector.collect(["BTC", "ETH", "SOL"])
        
        for p in prices:
            print(f"   ✅ {p.symbol}: ${p.price_usd:,.2f} ({p.price_change_24h or 0:+.2f}%)")
        
        print(f"\n📊 Coletando klines de {symbol}...")
        klines = await collector.get_klines(symbol, timeframe="1h", limit=5)
        
        if klines:
            print(f"   ✅ {len(klines)} candles coletados")
            latest = klines[-1]
            print(f"      Último: O={latest.open:.2f} H={latest.high:.2f} L={latest.low:.2f} C={latest.close:.2f}")
        
        metrics = collector.get_metrics()
        print(f"\n📈 Métricas:")
        print(f"   Binance - Requests: {metrics['binance']['total_requests']}, Taxa de sucesso: {metrics['binance']['success_rate']:.1f}%")
        
        print("\n✅ Price Collector: PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await collector.close()


async def test_whale_collector(symbol: str = "BTC") -> bool:
    print("\n" + "=" * 60)
    print("🐋 Testando Whale Collector")
    print("=" * 60)
    
    from src.collectors import WhaleCollector
    from src.config.settings import settings
    
    if not settings.whale_alert_api_key:
        print("\n⚠️  Whale Alert API key não configurada")
        print("   Configure WHALE_ALERT_API_KEY no .env para testar")
        print("\n⏭️  Whale Collector: PULADO")
        return True
    
    collector = WhaleCollector()
    
    try:
        health = await collector.health_check()
        print(f"\n🏥 Health Check: {health['status']}")
        
        print(f"\n🐋 Coletando transações whale de {symbol} (últimas 24h)...")
        whales = await collector.collect(symbols=[symbol], hours=24, min_usd=1_000_000)
        
        if whales:
            print(f"   ✅ {len(whales)} transações encontradas")
            for tx in whales[:3]:
                print(f"      • ${tx.amount_usd:,.0f} - {tx.transaction_type.value}")
        else:
            print("   ℹ️  Nenhuma transação grande nas últimas 24h")
        
        print(f"\n📊 Estatísticas de whale para {symbol}...")
        stats = await collector.get_stats_by_symbol(symbol, hours=24)
        print(f"   Total transações: {stats.get('total_transactions', 0)}")
        print(f"   Volume total: ${stats.get('total_volume_usd', 0):,.0f}")
        
        print("\n✅ Whale Collector: PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False
    finally:
        await collector.close()


async def test_news_collector(symbol: str = "BTC") -> bool:
    print("\n" + "=" * 60)
    print("📰 Testando News Collector")
    print("=" * 60)
    
    from src.collectors import NewsCollector
    from src.config.settings import settings
    
    collector = NewsCollector()
    
    try:
        health = await collector.health_check()
        print(f"\n🏥 Health Check: {health['status']}")
        
        if not settings.cryptopanic_api_key:
            print("\n⚠️  CryptoPanic API key não configurada")
        
        print(f"\n📰 Coletando notícias sobre {symbol} (últimas 24h)...")
        news = await collector.collect(symbols=[symbol], hours=24)
        
        if news:
            print(f"   ✅ {len(news)} notícias encontradas")
            for item in news[:3]:
                print(f"      • {item.title[:60]}...")
        else:
            print("   ℹ️  Nenhuma notícia encontrada")
        
        print(f"\n📊 Calculando score de narrativa para {symbol}...")
        score = await collector.get_narrative_score(symbol, hours=24)
        print(f"   Score: {score:.1f}/100")
        
        print("\n✅ News Collector: PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False
    finally:
        await collector.close()


async def test_oi_collector(symbol: str = "BTC") -> bool:
    print("\n" + "=" * 60)
    print("📊 Testando Open Interest Collector")
    print("=" * 60)
    
    from src.collectors import OpenInterestCollector
    
    collector = OpenInterestCollector()
    
    try:
        health = await collector.health_check()
        print(f"\n🏥 Health Check: {health['status']}")
        
        print(f"\n📊 Coletando Open Interest de {symbol}...")
        oi_data = await collector.collect_single(symbol)
        
        if oi_data:
            print(f"   ✅ Open Interest: {oi_data.open_interest:,.2f} contratos")
            print(f"      OI em USD: ${oi_data.open_interest_usd:,.0f}")
            if oi_data.funding_rate is not None:
                print(f"      Funding Rate: {oi_data.funding_rate:.4f}%")
        else:
            print(f"   ❌ Não foi possível coletar OI de {symbol}")
        
        print(f"\n📊 Calculando score de pressão de OI para {symbol}...")
        score = await collector.get_oi_pressure_score(symbol)
        if score is not None:
            print(f"   Score: {score:.1f}/100")
        
        print("\n✅ Open Interest Collector: PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False
    finally:
        await collector.close()


async def test_collector_manager(symbols: List[str]) -> bool:
    print("\n" + "=" * 60)
    print("🎛️  Testando Collector Manager")
    print("=" * 60)
    
    from src.collectors import CollectorManager
    
    manager = CollectorManager()
    
    try:
        print("\n🚀 Inicializando manager...")
        await manager.initialize()
        
        health = await manager.health_check()
        print(f"\n🏥 Health Check Geral: {health['status']}")
        print(f"   Fontes saudáveis: {health['healthy_sources']}/{health['total_sources']}")
        
        for source, status in health['sources'].items():
            if isinstance(status, dict):
                status_str = status.get('status', 'unknown')
                status_icon = "✅" if status_str in ['healthy', 'degraded'] else "❌"
                print(f"   {status_icon} {source}: {status_str}")
        
        print(f"\n📊 Executando coleta completa para {symbols}...")
        data = await manager.collect_all(symbols=symbols, include_news=True)
        
        print(f"\n📈 Resultados:")
        print(f"   Preços coletados: {len(data['prices'])}")
        print(f"   Transações whale: {len(data['whales'])}")
        print(f"   Dados de exchange flow: {len(data['exchange_flows'])}")
        print(f"   Dados de OI: {len(data['open_interest'])}")
        print(f"   Notícias: {len(data['news'])}")
        print(f"   Tempo total: {data['elapsed_seconds']:.2f}s")
        
        if data['errors']:
            print(f"\n⚠️  Erros: {len(data['errors'])}")
            for err in data['errors']:
                print(f"      • {err}")
        
        first_symbol = symbols[0]
        print(f"\n📊 Coletando dados detalhados para {first_symbol}...")
        symbol_data = await manager.collect_for_symbol(first_symbol)
        
        if symbol_data['price']:
            print(f"   💰 Preço: ${symbol_data['price'].price_usd:,.2f}")
        if symbol_data['open_interest']:
            print(f"   📊 OI: ${symbol_data['open_interest'].open_interest_usd:,.0f}")
        print(f"   🐋 Transações whale: {len(symbol_data['whales'])}")
        print(f"   📰 Notícias: {len(symbol_data['news'])}")
        
        print("\n📈 Métricas do Manager:")
        metrics = manager.get_metrics()
        print(f"   Cache entries: {metrics['cache']['entries']}")
        
        print("\n✅ Collector Manager: PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await manager.close()


async def main() -> int:
    parser = argparse.ArgumentParser(description="Teste dos coletores CryptoPulse")
    parser.add_argument("--collector", choices=["price", "whale", "news", "oi", "manager", "all"], default="all")
    parser.add_argument("--symbol", default="BTC")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧪 CryptoPulse - Teste de Coletores")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Símbolo: {args.symbol}")
    print(f"🔧 Coletor: {args.collector}")
    
    results: Dict[str, bool] = {}
    
    if args.collector in ["price", "all"]:
        results["price"] = await test_price_collector(args.symbol)
    
    if args.collector in ["whale", "all"]:
        results["whale"] = await test_whale_collector(args.symbol)
    
    if args.collector in ["news", "all"]:
        results["news"] = await test_news_collector(args.symbol)
    
    if args.collector in ["oi", "all"]:
        results["oi"] = await test_oi_collector(args.symbol)
    
    if args.collector in ["manager", "all"]:
        results["manager"] = await test_collector_manager([args.symbol, "ETH"])
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("⚠️  Alguns testes falharam")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
