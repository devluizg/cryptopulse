"""
CryptoPulse - Free Whale Collector
Combina Etherscan + Blockchain.com para rastrear baleias GRATUITAMENTE
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from src.collectors.onchain.etherscan_collector import EtherscanCollector
from src.collectors.onchain.blockchain_collector import BlockchainCollector
from src.utils.logger import logger


class FreeWhaleCollector:
    """
    Coletor unificado de transações de baleias.
    
    Combina dados de:
    - Etherscan (ETH) - Gratuito
    - Blockchain.com (BTC) - Gratuito
    """
    
    def __init__(self):
        self.eth_collector = EtherscanCollector()
        self.btc_collector = BlockchainCollector()
    
    async def health_check(self) -> Dict[str, str]:
        """Verifica status de todas as fontes."""
        eth_status = await self.eth_collector.health_check()
        btc_status = await self.btc_collector.health_check()
        
        overall = "healthy"
        if eth_status != "healthy" and btc_status != "healthy":
            overall = "unhealthy"
        elif eth_status != "healthy" or btc_status != "healthy":
            overall = "degraded"
        
        return {
            "overall": overall,
            "etherscan": eth_status,
            "blockchain_com": btc_status,
        }
    
    async def get_large_transactions(
        self,
        symbol: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtém transações grandes de baleias."""
        transactions: List[Dict[str, Any]] = []
        
        if symbol is None or symbol.upper() == "BTC":
            try:
                btc_txs = await self.btc_collector.get_large_transactions(
                    min_value_btc=10.0,
                    hours=hours,
                    limit=limit
                )
                transactions.extend(btc_txs)
                logger.info(f"Coletadas {len(btc_txs)} transações BTC")
            except Exception as e:
                logger.error(f"Erro ao coletar transações BTC: {e}")
        
        if symbol is None or symbol.upper() == "ETH":
            try:
                eth_txs = await self.eth_collector.get_large_transactions(
                    min_value_eth=100.0,
                    hours=hours,
                    limit=limit
                )
                transactions.extend(eth_txs)
                logger.info(f"Coletadas {len(eth_txs)} transações ETH")
            except Exception as e:
                logger.error(f"Erro ao coletar transações ETH: {e}")
        
        transactions.sort(key=lambda x: x["amount_usd"], reverse=True)
        return transactions[:limit]
    
    async def get_whale_stats(
        self,
        symbol: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Retorna estatísticas de atividade de baleias."""
        stats: Dict[str, Any] = {
            "total_transactions": 0,
            "total_volume_usd": 0.0,
            "exchange_inflow_usd": 0.0,
            "exchange_outflow_usd": 0.0,
            "netflow_usd": 0.0,
            "largest_transaction_usd": 0.0,
            "by_chain": {},
        }
        
        if symbol is None or symbol.upper() == "BTC":
            try:
                btc_stats = await self.btc_collector.get_whale_stats(hours)
                stats["by_chain"]["BTC"] = btc_stats
                stats["total_transactions"] += btc_stats["total_transactions"]
                stats["total_volume_usd"] += btc_stats["total_volume_usd"]
                stats["exchange_inflow_usd"] += btc_stats["exchange_inflow_usd"]
                stats["exchange_outflow_usd"] += btc_stats["exchange_outflow_usd"]
                if btc_stats["largest_transaction_usd"] > stats["largest_transaction_usd"]:
                    stats["largest_transaction_usd"] = btc_stats["largest_transaction_usd"]
            except Exception as e:
                logger.error(f"Erro ao obter stats BTC: {e}")
        
        if symbol is None or symbol.upper() == "ETH":
            try:
                eth_stats = await self.eth_collector.get_whale_stats(hours)
                stats["by_chain"]["ETH"] = eth_stats
                stats["total_transactions"] += eth_stats["total_transactions"]
                stats["total_volume_usd"] += eth_stats["total_volume_usd"]
                stats["exchange_inflow_usd"] += eth_stats["exchange_inflow_usd"]
                stats["exchange_outflow_usd"] += eth_stats["exchange_outflow_usd"]
                if eth_stats["largest_transaction_usd"] > stats["largest_transaction_usd"]:
                    stats["largest_transaction_usd"] = eth_stats["largest_transaction_usd"]
            except Exception as e:
                logger.error(f"Erro ao obter stats ETH: {e}")
        
        stats["netflow_usd"] = stats["exchange_inflow_usd"] - stats["exchange_outflow_usd"]
        return stats
    
    async def calculate_whale_score(
        self,
        symbol: str,
        hours: int = 24
    ) -> float:
        """Calcula score de atividade de baleias (0-100)."""
        if symbol.upper() not in ["BTC", "ETH"]:
            return 50.0
        
        try:
            stats = await self.get_whale_stats(symbol=symbol, hours=hours)
            
            if stats["total_transactions"] == 0:
                return 50.0
            
            score = 50.0
            
            # Fator 1: Volume
            volume_millions = stats["total_volume_usd"] / 1_000_000
            if volume_millions >= 100:
                score += 20
            elif volume_millions >= 10:
                score += 10
            elif volume_millions >= 1:
                score += 5
            
            # Fator 2: Número de transações
            if stats["total_transactions"] >= 50:
                score += 10
            elif stats["total_transactions"] >= 20:
                score += 5
            elif stats["total_transactions"] >= 5:
                score += 2
            
            # Fator 3: Netflow
            netflow_millions = stats["netflow_usd"] / 1_000_000
            if netflow_millions <= -50:
                score += 20
            elif netflow_millions <= -10:
                score += 15
            elif netflow_millions <= -1:
                score += 10
            elif netflow_millions >= 50:
                score -= 15
            elif netflow_millions >= 10:
                score -= 10
            elif netflow_millions >= 1:
                score -= 5
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Erro ao calcular whale score: {e}")
            return 50.0
    
    async def close(self):
        """Fecha todas as conexões."""
        await self.eth_collector.close()
        await self.btc_collector.close()
