#!/usr/bin/env python3
"""
CryptoPulse - Seed Script
Popula o banco com os ativos iniciais para monitoramento
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório `backend` ao `sys.path` para que os imports funcionem
# Se este script está em `cryptopulse/scripts/seed_assets.py`, então
# `Path(__file__).resolve().parents[0]` é `cryptopulse/scripts/`
# `Path(__file__).resolve().parents[1]` é `cryptopulse/`
# Queremos adicionar `cryptopulse/backend`
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import select
from src.database.connection import async_session_maker, engine
from src.database.models import Asset


# Lista de ativos iniciais para monitorar
INITIAL_ASSETS = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "coingecko_id": "bitcoin",
        "binance_symbol": "BTCUSDT",
        "priority": 100,
        "description": "A primeira e maior criptomoeda por capitalização de mercado."
    },
    {
        "symbol": "ETH",
        "name": "Ethereum",
        "coingecko_id": "ethereum",
        "binance_symbol": "ETHUSDT",
        "priority": 90,
        "description": "Plataforma de contratos inteligentes líder do mercado."
    },
    {
        "symbol": "SOL",
        "name": "Solana",
        "coingecko_id": "solana",
        "binance_symbol": "SOLUSDT",
        "priority": 80,
        "description": "Blockchain de alta performance conhecida por baixas taxas."
    },
    {
        "symbol": "BNB",
        "name": "BNB",
        "coingecko_id": "binancecoin",
        "binance_symbol": "BNBUSDT",
        "priority": 70,
        "description": "Token nativo da Binance Smart Chain."
    },
    {
        "symbol": "XRP",
        "name": "XRP",
        "coingecko_id": "ripple",
        "binance_symbol": "XRPUSDT",
        "priority": 65,
        "description": "Criptomoeda focada em pagamentos internacionais."
    },
    {
        "symbol": "ADA",
        "name": "Cardano",
        "coingecko_id": "cardano",
        "binance_symbol": "ADAUSDT",
        "priority": 60,
        "description": "Blockchain proof-of-stake com foco em pesquisa acadêmica."
    },
    {
        "symbol": "DOGE",
        "name": "Dogecoin",
        "coingecko_id": "dogecoin",
        "binance_symbol": "DOGEUSDT",
        "priority": 55,
        "description": "Memecoin original, popular por influência de Elon Musk."
    },
    {
        "symbol": "AVAX",
        "name": "Avalanche",
        "coingecko_id": "avalanche-2",
        "binance_symbol": "AVAXUSDT",
        "priority": 50,
        "description": "Plataforma de contratos inteligentes de alta velocidade."
    },
    {
        "symbol": "LINK",
        "name": "Chainlink",
        "coingecko_id": "chainlink",
        "binance_symbol": "LINKUSDT",
        "priority": 45,
        "description": "Rede de oráculos descentralizados líder do mercado."
    },
    {
        "symbol": "MATIC",
        "name": "Polygon",
        "coingecko_id": "matic-network",
        "binance_symbol": "MATICUSDT",
        "priority": 40,
        "description": "Solução de escalabilidade Layer 2 para Ethereum."
    },
]


async def seed_assets():
    """Popula o banco com os ativos iniciais"""
    
    print("\n🌱 CryptoPulse - Seed Script")
    print("=" * 50)
    
    async with async_session_maker() as session:
        # Verificar ativos existentes
        result = await session.execute(select(Asset.symbol))
        existing_symbols = {row[0] for row in result.fetchall()}
        
        added = 0
        skipped = 0
        
        for asset_data in INITIAL_ASSETS:
            if asset_data["symbol"] in existing_symbols:
                print(f"  ⏭️  {asset_data['symbol']}: já existe")
                skipped += 1
                continue
            
            asset = Asset(**asset_data)
            session.add(asset)
            print(f"  ✅ {asset_data['symbol']}: adicionado")
            added += 1
        
        await session.commit()
        
        print("=" * 50)
        print(f"📊 Resultado: {added} adicionados, {skipped} ignorados")
        print()


async def list_assets():
    """Lista todos os ativos no banco"""
    
    print("\n📋 Ativos Cadastrados:")
    print("=" * 50)
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(Asset).order_by(Asset.priority.desc())
        )
        assets = result.scalars().all()
        
        if not assets:
            print("  Nenhum ativo cadastrado.")
        else:
            for asset in assets:
                status = "🟢" if asset.is_active else "🔴"
                print(f"  {status} {asset.symbol:6} | {asset.name:15} | Priority: {asset.priority}")
        
        print("=" * 50)
        print(f"Total: {len(assets)} ativos")
        print()


async def main():
    """Função principal"""
    
    # Seed dos ativos
    await seed_assets()
    
    # Listar ativos
    await list_assets()
    
    # Fechar conexões
    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nOperação cancelada.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        raise
