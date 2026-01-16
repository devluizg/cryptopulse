"""
Script para popular histórico de preços e volumes.

Busca os últimos 7 dias de candles 1h da Binance e salva no banco.
Isso permite que o indicador de Volume Anomaly funcione corretamente.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.database.connection import async_session_maker
from src.database.repositories import AssetRepository, PriceRepository
from src.collectors.price_collector import PriceCollector


async def populate_history():
    """Popula histórico de preços para todos os ativos."""
    
    print("=" * 60)
    print("📊 Populando Histórico de Preços e Volume")
    print("=" * 60)
    print()
    
    collector = PriceCollector()
    
    async with async_session_maker() as session:
        asset_repo = AssetRepository(session)
        price_repo = PriceRepository(session)
        
        # Buscar ativos ativos
        assets = await asset_repo.get_active_assets()
        print(f"📋 {len(assets)} ativos para processar")
        print()
        
        total_saved = 0
        
        for asset in assets:
            symbol = asset.symbol
            print(f"🔄 Processando {symbol}...", end=" ")
            
            try:
                # Buscar últimos 168 candles de 1h (7 dias)
                klines = await collector.get_klines(
                    symbol=symbol,
                    timeframe="1h",
                    limit=168  # 7 dias * 24 horas
                )
                
                if not klines:
                    print(f"⚠️ Sem dados")
                    continue
                
                saved = 0
                for candle in klines:
                    try:
                        await price_repo.upsert_price(
                            asset_id=asset.id,
                            timestamp=candle.timestamp,
                            timeframe="1h",
                            open_price=candle.open,
                            high_price=candle.high,
                            low_price=candle.low,
                            close_price=candle.close,
                            volume=candle.volume,
                            source="binance",
                        )
                        saved += 1
                    except Exception as e:
                        logger.debug(f"Erro ao salvar candle: {e}")
                
                total_saved += saved
                print(f"✅ {saved} candles salvos")
                
            except Exception as e:
                print(f"❌ Erro: {e}")
            
            # Pequena pausa para não sobrecarregar a API
            await asyncio.sleep(0.2)
        
        # Commit final
        await session.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Total: {total_saved} candles salvos no banco")
        print("=" * 60)
    
    await collector.close()


async def verify_history():
    """Verifica o histórico salvo."""
    
    print()
    print("📊 Verificando histórico salvo...")
    print()
    
    async with async_session_maker() as session:
        asset_repo = AssetRepository(session)
        price_repo = PriceRepository(session)
        
        assets = await asset_repo.get_active_assets()
        
        for asset in assets:
            # Buscar histórico das últimas 168 horas (7 dias)
            history = await price_repo.get_history(
                asset_id=asset.id,
                hours=168,
                timeframe="1h"
            )
            
            if history:
                volumes = [p.volume for p in history if p.volume]
                avg_vol = sum(volumes) / len(volumes) if volumes else 0
                print(f"  {asset.symbol}: {len(history)} candles, vol médio: ${avg_vol:,.0f}")
            else:
                print(f"  {asset.symbol}: ❌ Sem histórico")


async def main():
    """Executa o script completo."""
    await populate_history()
    await verify_history()


if __name__ == "__main__":
    asyncio.run(main())
