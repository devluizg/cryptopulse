#!/usr/bin/env python3
"""
CryptoPulse - Teste dos Coletores de Whale Gratuitos
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.collectors.onchain import (
    EtherscanCollector,
    BlockchainCollector,
    FreeWhaleCollector,
)
from src.config.settings import settings


async def test_etherscan():
    """Testa o coletor Etherscan."""
    print("\n" + "=" * 60)
    print("🔷 Testando Etherscan Collector (ETH)")
    print("=" * 60)
    
    collector = EtherscanCollector()
    
    # Verificar se API key está configurada
    if not collector.is_available():
        print("\n⚠️  Etherscan API key não configurada!")
        print("   Para habilitar, obtenha uma key gratuita em:")
        print("   https://etherscan.io/myapikey")
        print(f"\n   Depois adicione no .env:")
        print(f"   ETHERSCAN_API_KEY=sua_chave")
        print("\n⏭️  Etherscan Collector: PULADO (sem API key)")
        await collector.close()
        return True  # Não é erro, apenas não configurado
    
    try:
        # Health check
        health = await collector.health_check()
        print(f"\n🏥 Health: {health}")
        
        if health != "healthy":
            print("⚠️  API não está saudável, pulando testes detalhados")
            await collector.close()
            return True
        
        # Preço ETH
        price = await collector.get_eth_price()
        print(f"💰 Preço ETH: ${price:,.2f}" if price else "❌ Preço não disponível")
        
        # Transações grandes
        print("\n📊 Buscando transações grandes...")
        transactions = await collector.get_large_transactions(
            min_value_eth=50.0,
            hours=24,
            limit=10
        )
        
        print(f"\n🐋 Encontradas {len(transactions)} transações de baleias ETH:")
        for i, tx in enumerate(transactions[:5], 1):
            print(f"\n   {i}. {tx['tx_hash'][:16]}...")
            print(f"      💵 Valor: {tx['amount']:.2f} ETH (${tx['amount_usd']:,.0f})")
            print(f"      📤 De: {tx['from_owner']}")
            print(f"      📥 Para: {tx['to_owner']}")
            print(f"      🏷️  Tipo: {tx['transaction_type']}")
        
        print("\n✅ Etherscan Collector: PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await collector.close()


async def test_blockchain():
    """Testa o coletor Blockchain.com."""
    print("\n" + "=" * 60)
    print("🟠 Testando Blockchain.com Collector (BTC)")
    print("=" * 60)
    
    collector = BlockchainCollector()
    
    try:
        # Health check
        health = await collector.health_check()
        print(f"\n🏥 Health: {health}")
        
        # Preço BTC
        price = await collector.get_btc_price()
        print(f"💰 Preço BTC: ${price:,.2f}" if price else "❌ Preço não disponível")
        
        # Transações grandes
        print("\n📊 Buscando transações grandes (pode demorar ~30s)...")
        transactions = await collector.get_large_transactions(
            min_value_btc=5.0,
            hours=24,
            limit=10
        )
        
        print(f"\n🐋 Encontradas {len(transactions)} transações de baleias BTC:")
        for i, tx in enumerate(transactions[:5], 1):
            print(f"\n   {i}. {tx['tx_hash'][:16]}...")
            print(f"      💵 Valor: {tx['amount']:.4f} BTC (${tx['amount_usd']:,.0f})")
            print(f"      📤 De: {tx['from_owner']}")
            print(f"      📥 Para: {tx['to_owner']}")
            print(f"      🏷️  Tipo: {tx['transaction_type']}")
        
        # Stats
        if transactions:
            print("\n📈 Estatísticas de baleias BTC (24h):")
            stats = await collector.get_whale_stats(hours=24)
            print(f"   Total de transações: {stats['total_transactions']}")
            print(f"   Volume total: ${stats['total_volume_usd']:,.0f}")
            print(f"   Netflow: ${stats['netflow_usd']:,.0f}")
        
        print("\n✅ Blockchain.com Collector: PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await collector.close()


async def test_unified():
    """Testa o coletor unificado."""
    print("\n" + "=" * 60)
    print("🌐 Testando Free Whale Collector (Unificado)")
    print("=" * 60)
    
    collector = FreeWhaleCollector()
    
    try:
        # Health check
        health = await collector.health_check()
        print(f"\n🏥 Health Check:")
        print(f"   Overall: {health['overall']}")
        print(f"   Etherscan: {health['etherscan']}")
        print(f"   Blockchain.com: {health['blockchain_com']}")
        
        # Scores
        print("\n📊 Calculando Whale Scores:")
        btc_score = await collector.calculate_whale_score("BTC")
        eth_score = await collector.calculate_whale_score("ETH")
        sol_score = await collector.calculate_whale_score("SOL")
        
        print(f"   🟠 BTC Whale Score: {btc_score:.1f}/100")
        print(f"   🔷 ETH Whale Score: {eth_score:.1f}/100")
        print(f"   🟣 SOL Whale Score: {sol_score:.1f}/100 (não suportado, neutro)")
        
        print("\n✅ Free Whale Collector: PASSOU")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await collector.close()


async def main():
    print("\n" + "=" * 60)
    print("🧪 CryptoPulse - Teste de Whale Collectors Gratuitos")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Mostrar status das API keys
    print("\n📋 Status das API Keys:")
    etherscan_key = settings.etherscan_api_key
    print(f"   ETHERSCAN_API_KEY: {'✅ Configurada' if etherscan_key else '❌ Não configurada'}")
    print(f"   BLOCKCHAIN.COM: ✅ Não requer API key")
    
    results = {}
    
    # Testar Blockchain.com primeiro (não precisa de key)
    results["blockchain"] = await test_blockchain()
    
    # Testar Etherscan
    results["etherscan"] = await test_etherscan()
    
    # Testar Unificado
    results["unified"] = await test_unified()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    for name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"   {name}: {status}")
    
    all_passed = all(results.values())
    print("=" * 60)
    if all_passed:
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️  Alguns testes falharam")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste cancelado pelo usuário")
        sys.exit(1)
