#!/usr/bin/env python3
"""
CryptoPulse - Test Repositories
Testa as operações básicas dos repositórios
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database.connection import async_session_maker, engine
from src.database.repositories import (
    AssetRepository,
    ScoreRepository,
    AlertRepository,
    WhaleRepository,
    PriceRepository,
)


async def test_asset_repository():
    """Testa AssetRepository"""
    print("\n📦 Testando AssetRepository...")
    
    async with async_session_maker() as session:
        repo = AssetRepository(session)
        
        # Buscar todos
        assets = await repo.get_active_assets()
        print(f"  ✅ get_active_assets(): {len(assets)} ativos")
        
        # Buscar por símbolo
        btc = await repo.get_by_symbol("BTC")
        if btc:
            print(f"  ✅ get_by_symbol('BTC'): {btc.name}")
        
        # Buscar símbolos
        symbols = await repo.get_symbols()
        print(f"  ✅ get_symbols(): {symbols}")
        
        # Mapa símbolo -> ID
        symbol_map = await repo.get_symbol_id_map()
        print(f"  ✅ get_symbol_id_map(): {len(symbol_map)} mapeamentos")
        
        # Contar
        count = await repo.count()
        print(f"  ✅ count(): {count} ativos")


async def test_score_repository():
    """Testa ScoreRepository"""
    print("\n📊 Testando ScoreRepository...")
    
    async with async_session_maker() as session:
        asset_repo = AssetRepository(session)
        score_repo = ScoreRepository(session)
        
        # Pegar ID do BTC
        btc = await asset_repo.get_by_symbol("BTC")
        if not btc:
            print("  ⚠️ BTC não encontrado, pulando testes de score")
            return
        
        # Criar um score de teste
        score = await score_repo.create_score(
            asset_id=btc.id,
            explosion_score=65.5,
            status="attention",
            whale_score=70.0,
            netflow_score=60.0,
            volume_score=65.0,
            oi_score=55.0,
            narrative_score=75.0,
            price_usd=45000.0,
            price_change_24h=2.5
        )
        await session.commit()
        print(f"  ✅ create_score(): Score ID {score.id} criado")
        
        # Buscar score mais recente
        latest = await score_repo.get_latest_by_symbol("BTC")
        if latest:
            print(f"  ✅ get_latest_by_symbol(): Score {latest.explosion_score}")
        
        # Buscar todos os últimos
        all_latest = await score_repo.get_all_latest()
        print(f"  ✅ get_all_latest(): {len(all_latest)} scores")


async def test_alert_repository():
    """Testa AlertRepository"""
    print("\n🚨 Testando AlertRepository...")
    
    async with async_session_maker() as session:
        asset_repo = AssetRepository(session)
        alert_repo = AlertRepository(session)
        
        btc = await asset_repo.get_by_symbol("BTC")
        if not btc:
            print("  ⚠️ BTC não encontrado, pulando testes de alerta")
            return
        
        # Criar alerta de teste
        alert = await alert_repo.create_alert(
            asset_id=btc.id,
            alert_type="score_threshold",
            severity="warning",
            title="BTC atingiu zona de atenção",
            message="O score de explosão do Bitcoin atingiu 65.5 pontos.",
            score_at_trigger=65.5,
            price_at_trigger=45000.0
        )
        await session.commit()
        print(f"  ✅ create_alert(): Alerta ID {alert.id} criado")
        
        # Contar não lidos
        unread = await alert_repo.count_unread()
        print(f"  ✅ count_unread(): {unread} alertas não lidos")
        
        # Marcar como lido
        await alert_repo.mark_as_read(alert.id)
        await session.commit()
        print(f"  ✅ mark_as_read(): Alerta marcado como lido")


async def test_whale_repository():
    """Testa WhaleRepository"""
    print("\n🐋 Testando WhaleRepository...")
    
    async with async_session_maker() as session:
        asset_repo = AssetRepository(session)
        whale_repo = WhaleRepository(session)
        
        btc = await asset_repo.get_by_symbol("BTC")
        if not btc:
            print("  ⚠️ BTC não encontrado, pulando testes de whale")
            return
        
        # Criar transação de teste
        tx = await whale_repo.create_transaction(
            asset_id=btc.id,
            amount=100.0,
            amount_usd=4_500_000.0,
            transaction_type="exchange_withdrawal",
            timestamp=datetime.utcnow(),
            from_owner="binance",
            to_owner="unknown"
        )
        await session.commit()
        print(f"  ✅ create_transaction(): TX ID {tx.id} criada")
        
        # Buscar transações recentes
        recent = await whale_repo.get_recent(hours=24)
        print(f"  ✅ get_recent(): {len(recent)} transações")
        
        # Estatísticas
        stats = await whale_repo.get_stats_by_asset(btc.id, hours=24)
        print(f"  ✅ get_stats_by_asset(): {stats}")


async def test_price_repository():
    """Testa PriceRepository"""
    print("\n💰 Testando PriceRepository...")
    
    async with async_session_maker() as session:
        asset_repo = AssetRepository(session)
        price_repo = PriceRepository(session)
        
        btc = await asset_repo.get_by_symbol("BTC")
        if not btc:
            print("  ⚠️ BTC não encontrado, pulando testes de preço")
            return
        
        # Criar preço de teste
        price = await price_repo.create_price(
            asset_id=btc.id,
            open=44500.0,
            high=45500.0,
            low=44000.0,
            close=45000.0,
            volume=1_500_000_000.0,
            timestamp=datetime.utcnow(),
            timeframe="1h",
            source="binance"
        )
        await session.commit()
        print(f"  ✅ create_price(): Price ID {price.id} criado")
        
        # Buscar preço mais recente
        latest = await price_repo.get_latest(btc.id)
        if latest:
            print(f"  ✅ get_latest(): ${latest.close:,.2f}")


async def main():
    print("\n" + "=" * 60)
    print("🧪 CryptoPulse - Teste de Repositórios")
    print("=" * 60)
    
    try:
        await test_asset_repository()
        await test_score_repository()
        await test_alert_repository()
        await test_whale_repository()
        await test_price_repository()
        
        print("\n" + "=" * 60)
        print("✅ Todos os testes passaram!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
