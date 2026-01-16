"""
Whale Collector - Coleta transações de grandes holders.

Usa APIs gratuitas:
- Etherscan (ETH) - Requer API key gratuita
- Blockchain.com (BTC) - Sem necessidade de API key
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger

from src.collectors.base_collector import BaseCollector, APIError
from src.collectors.onchain.etherscan_collector import EtherscanCollector
from src.collectors.onchain.blockchain_collector import BlockchainCollector
from src.config.settings import settings


class TransactionType(str, Enum):
    EXCHANGE_DEPOSIT = "exchange_deposit"
    EXCHANGE_WITHDRAWAL = "exchange_withdrawal"
    WALLET_TRANSFER = "wallet_transfer"
    UNKNOWN = "unknown"


@dataclass
class WhaleTransaction:
    tx_hash: str
    symbol: str
    amount: float
    amount_usd: float
    transaction_type: TransactionType
    from_address: str
    to_address: str
    from_owner: Optional[str] = None
    to_owner: Optional[str] = None
    blockchain: str = "ethereum"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "unknown"
    
    @property
    def is_exchange_inflow(self) -> bool:
        """Retorna True se é entrada em exchange (bearish)."""
        return self.transaction_type == TransactionType.EXCHANGE_DEPOSIT
    
    @property
    def is_exchange_outflow(self) -> bool:
        """Retorna True se é saída de exchange (bullish)."""
        return self.transaction_type == TransactionType.EXCHANGE_WITHDRAWAL
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_hash": self.tx_hash,
            "symbol": self.symbol,
            "amount": self.amount,
            "amount_usd": self.amount_usd,
            "transaction_type": self.transaction_type.value,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "from_owner": self.from_owner,
            "to_owner": self.to_owner,
            "blockchain": self.blockchain,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "is_exchange_inflow": self.is_exchange_inflow,
            "is_exchange_outflow": self.is_exchange_outflow,
        }


class WhaleAlertCollector(BaseCollector[WhaleTransaction]):
    """Coletor de transações do Whale Alert (API paga - backup)."""
    
    BASE_URL = "https://api.whale-alert.io/v1"
    DEFAULT_RATE_LIMIT_DELAY = 2.0
    EXCHANGE_KEYWORDS = ["binance", "coinbase", "kraken", "huobi", "okex", "kucoin"]
    
    def __init__(self):
        api_key = settings.whale_alert_api_key
        if not api_key:
            logger.debug("Whale Alert API key não configurada")
        
        super().__init__(
            name="whale_alert",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit_delay=self.DEFAULT_RATE_LIMIT_DELAY,
        )
    
    def _is_exchange(self, owner: Optional[str]) -> bool:
        if not owner:
            return False
        return any(kw in owner.lower() for kw in self.EXCHANGE_KEYWORDS)
    
    def _classify_transaction(self, from_owner: Optional[str], to_owner: Optional[str]) -> TransactionType:
        if self._is_exchange(from_owner) and not self._is_exchange(to_owner):
            return TransactionType.EXCHANGE_WITHDRAWAL
        elif not self._is_exchange(from_owner) and self._is_exchange(to_owner):
            return TransactionType.EXCHANGE_DEPOSIT
        return TransactionType.WALLET_TRANSFER
    
    async def collect(
        self, symbols: Optional[List[str]] = None, min_usd: float = 500000, hours: int = 24
    ) -> List[WhaleTransaction]:
        if not self.api_key:
            return []
        
        end_time = int(datetime.utcnow().timestamp())
        start_time = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())
        
        try:
            response = await self.get("transactions", params={
                "api_key": self.api_key,
                "start": start_time,
                "end": end_time,
                "min_value": min_usd,
                "limit": 100,
            })
            
            results: List[WhaleTransaction] = []
            transactions = response.get("transactions", []) if isinstance(response, dict) else []
            
            for tx in transactions:
                if not isinstance(tx, dict):
                    continue
                
                symbol = tx.get("symbol", "").upper()
                if symbols and symbol not in [s.upper() for s in symbols]:
                    continue
                
                from_info = tx.get("from", {}) or {}
                to_info = tx.get("to", {}) or {}
                
                whale_tx = WhaleTransaction(
                    tx_hash=tx.get("hash", ""),
                    symbol=symbol,
                    amount=float(tx.get("amount", 0)),
                    amount_usd=float(tx.get("amount_usd", 0)),
                    transaction_type=self._classify_transaction(
                        from_info.get("owner"),
                        to_info.get("owner")
                    ),
                    from_address=from_info.get("address", ""),
                    to_address=to_info.get("address", ""),
                    from_owner=from_info.get("owner"),
                    to_owner=to_info.get("owner"),
                    blockchain=tx.get("blockchain", "unknown"),
                    timestamp=datetime.utcfromtimestamp(tx.get("timestamp", 0)),
                    source="whale_alert",
                )
                results.append(whale_tx)
            
            return results
            
        except APIError as e:
            self.logger.error(f"Erro Whale Alert: {e}")
            return []
    
    async def collect_single(self, symbol: str) -> Optional[WhaleTransaction]:
        txs = await self.collect(symbols=[symbol], hours=24)
        return txs[0] if txs else None
    
    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "unavailable", "collector": self.name}
        try:
            await self.get("status", params={"api_key": self.api_key})
            return {"status": "healthy", "collector": self.name}
        except:
            return {"status": "unhealthy", "collector": self.name}


class WhaleCollector:
    """
    Agregador de coletores de whale.
    
    Fontes:
    1. Etherscan (ETH) - Gratuito com API key
    2. Blockchain.com (BTC) - Gratuito (rate limit alto)
    """
    
    # Configurações de coleta ajustadas para realidade
    DEFAULT_MIN_ETH = 10.0       # ~$33k - captura mais transações
    DEFAULT_MIN_BTC = 5.0        # ~$475k
    DEFAULT_HOURS = 48           # 2 dias de janela
    
    # Mapeamento de símbolos para blockchains
    SYMBOL_TO_BLOCKCHAIN = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "LINK": "ethereum",
        "MATIC": "ethereum",
        "UNI": "ethereum",
        "AAVE": "ethereum",
        # Sem suporte direto (retorna neutro)
        "SOL": None,
        "BNB": None,
        "XRP": None,
        "ADA": None,
        "DOGE": None,
        "AVAX": None,
    }
    
    def __init__(self):
        self.etherscan = EtherscanCollector()
        self.blockchain_com = BlockchainCollector()
        self.whale_alert = WhaleAlertCollector()
        self.logger = logger.bind(collector="whale_aggregator")
        
        if self.etherscan.is_available():
            self.logger.info("✅ Etherscan disponível (ETH)")
        else:
            self.logger.warning("⚠️ Etherscan: sem API key")
        
        self.logger.info("✅ Blockchain.com disponível (BTC - rate limit alto)")
    
    async def close(self):
        """Fecha todas as conexões."""
        await self.etherscan.close()
        await self.blockchain_com.close()
        await self.whale_alert.close()
    
    def _get_blockchain(self, symbol: str) -> Optional[str]:
        """Retorna a blockchain de um símbolo."""
        return self.SYMBOL_TO_BLOCKCHAIN.get(symbol.upper())
    
    def _convert_to_whale_transaction(self, tx: Dict[str, Any], source: str) -> WhaleTransaction:
        """Converte transação do formato interno para WhaleTransaction."""
        tx_type_str = tx.get("transaction_type", "unknown")
        
        if tx_type_str == "exchange_deposit":
            tx_type = TransactionType.EXCHANGE_DEPOSIT
        elif tx_type_str == "exchange_withdrawal":
            tx_type = TransactionType.EXCHANGE_WITHDRAWAL
        elif tx_type_str == "transfer":
            tx_type = TransactionType.WALLET_TRANSFER
        else:
            tx_type = TransactionType.UNKNOWN
        
        timestamp = tx.get("timestamp")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except:
                timestamp = datetime.utcnow()
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.utcnow()
        
        # Remover timezone para consistência
        if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)
        
        return WhaleTransaction(
            tx_hash=tx.get("tx_hash", ""),
            symbol=tx.get("symbol", ""),
            amount=float(tx.get("amount", 0)),
            amount_usd=float(tx.get("amount_usd", 0)),
            transaction_type=tx_type,
            from_address=tx.get("from_address", ""),
            to_address=tx.get("to_address", ""),
            from_owner=tx.get("from_owner"),
            to_owner=tx.get("to_owner"),
            blockchain=tx.get("blockchain", "unknown"),
            timestamp=timestamp,
            source=source,
        )
    
    async def collect(
        self, 
        symbols: Optional[List[str]] = None, 
        min_usd: float = 30000,  # Reduzido para capturar mais
        hours: int = 48          # Janela maior
    ) -> List[WhaleTransaction]:
        """
        Coleta transações de whale de múltiplas fontes.
        """
        all_transactions: List[WhaleTransaction] = []
        
        if symbols is None:
            symbols = ["BTC", "ETH"]
        
        symbols_upper = [s.upper() for s in symbols]
        
        # Coletar ETH via Etherscan (mais confiável)
        if "ETH" in symbols_upper and self.etherscan.is_available():
            try:
                eth_price = await self.etherscan.get_eth_price() or 3200
                min_eth = max(min_usd / eth_price, self.DEFAULT_MIN_ETH)
                
                self.logger.debug(f"Coletando ETH: min={min_eth:.1f} ETH, hours={hours}")
                
                eth_txs = await self.etherscan.get_large_transactions(
                    min_value_eth=min_eth,
                    hours=hours,
                    limit=100
                )
                
                for tx in eth_txs:
                    whale_tx = self._convert_to_whale_transaction(tx, "etherscan")
                    all_transactions.append(whale_tx)
                
                self.logger.info(f"Etherscan: {len(eth_txs)} transações ETH")
                
            except Exception as e:
                self.logger.error(f"Erro Etherscan: {e}")
        
        # Coletar BTC via Blockchain.com (tem rate limit)
        if "BTC" in symbols_upper:
            try:
                btc_price = await self.blockchain_com.get_btc_price() or 95000
                min_btc = max(min_usd / btc_price, self.DEFAULT_MIN_BTC)
                
                self.logger.debug(f"Coletando BTC: min={min_btc:.1f} BTC, hours={hours}")
                
                btc_txs = await self.blockchain_com.get_large_transactions(
                    min_value_btc=min_btc,
                    hours=hours,
                    limit=50
                )
                
                for tx in btc_txs:
                    whale_tx = self._convert_to_whale_transaction(tx, "blockchain.com")
                    all_transactions.append(whale_tx)
                
                self.logger.info(f"Blockchain.com: {len(btc_txs)} transações BTC")
                
            except Exception as e:
                self.logger.error(f"Erro Blockchain.com: {e}")
        
        # Ordenar por valor USD
        all_transactions.sort(key=lambda x: x.amount_usd, reverse=True)
        
        self.logger.info(f"Total: {len(all_transactions)} transações whale")
        return all_transactions
    
    async def get_stats_by_symbol(self, symbol: str, hours: int = 48) -> Dict[str, Any]:
        """Retorna estatísticas de whale para um símbolo."""
        symbol = symbol.upper()
        blockchain = self._get_blockchain(symbol)
        
        if blockchain == "ethereum" and self.etherscan.is_available():
            try:
                stats = await self.etherscan.get_whale_stats(hours)
                return {
                    "total_transactions": stats.get("total_transactions", 0),
                    "total_volume_usd": stats.get("total_volume_usd", 0),
                    "exchange_deposits": 0,
                    "exchange_withdrawals": 0,
                    "exchange_deposits_usd": stats.get("exchange_inflow_usd", 0),
                    "exchange_withdrawals_usd": stats.get("exchange_outflow_usd", 0),
                    "net_flow_usd": stats.get("netflow_usd", 0),
                    "source": "etherscan",
                }
            except Exception as e:
                self.logger.error(f"Erro stats ETH: {e}")
        
        elif blockchain == "bitcoin":
            try:
                stats = await self.blockchain_com.get_whale_stats(hours)
                return {
                    "total_transactions": stats.get("total_transactions", 0),
                    "total_volume_usd": stats.get("total_volume_usd", 0),
                    "exchange_deposits": 0,
                    "exchange_withdrawals": 0,
                    "exchange_deposits_usd": stats.get("exchange_inflow_usd", 0),
                    "exchange_withdrawals_usd": stats.get("exchange_outflow_usd", 0),
                    "net_flow_usd": stats.get("netflow_usd", 0),
                    "source": "blockchain.com",
                }
            except Exception as e:
                self.logger.error(f"Erro stats BTC: {e}")
        
        # Sem suporte
        return {
            "total_transactions": 0,
            "total_volume_usd": 0,
            "exchange_deposits": 0,
            "exchange_withdrawals": 0,
            "exchange_deposits_usd": 0,
            "exchange_withdrawals_usd": 0,
            "net_flow_usd": 0,
            "source": "none",
            "note": f"{symbol} sem dados on-chain disponíveis"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas dos coletores."""
        return {
            "etherscan": {"available": self.etherscan.is_available()},
            "blockchain_com": {"available": True},
            "whale_alert": {"available": bool(self.whale_alert.api_key)},
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde das fontes."""
        eth_status = "unavailable"
        if self.etherscan.is_available():
            eth_status = await self.etherscan.health_check()
        
        btc_status = await self.blockchain_com.health_check()
        
        # Status geral
        if eth_status == "healthy":
            overall = "healthy"
        elif btc_status == "healthy":
            overall = "degraded"
        else:
            overall = "unhealthy"
        
        return {
            "status": overall,
            "sources": {
                "etherscan": eth_status,
                "blockchain_com": btc_status,
            }
        }
