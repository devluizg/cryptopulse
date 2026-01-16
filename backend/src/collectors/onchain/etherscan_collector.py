"""
CryptoPulse - Etherscan Collector V2
Coleta transações grandes de ETH usando a API V2 do Etherscan
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

import httpx

from src.config.settings import settings
from src.utils.logger import logger


class EtherscanCollector:
    """
    Coletor de transações grandes de Ethereum via Etherscan API V2.
    
    API Gratuita (com key):
    - 5 requests/segundo
    - Histórico completo
    - Requer API key gratuita: https://etherscan.io/myapikey
    """
    
    BASE_URL = "https://api.etherscan.io/v2/api"
    CHAIN_ID = 1  # Ethereum Mainnet
    
    # Parâmetros padrão mais realistas
    DEFAULT_MIN_ETH: float = 10.0      # ~$33k
    DEFAULT_HOURS: int = 48            # 2 dias
    
    KNOWN_EXCHANGES: Dict[str, str] = {
        "0x28c6c06298d514db089934071355e5743bf21d60": "binance",
        "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "binance",
        "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "binance",
        "0x56eddb7aa87536c09ccc2793473599fd21a8b17f": "binance",
        "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8": "binance",
        "0xf977814e90da44bfa03b6295a0616a897441acec": "binance",
        "0x503828976d22510aad0201ac7ec88293211d23da": "coinbase",
        "0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740": "coinbase",
        "0x3cd751e6b0078be393132286c442345e5dc49699": "coinbase",
        "0xb5d85cbf7cb3ee0d56b3bb207d5fc4b82f43f511": "coinbase",
        "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0": "kraken",
        "0xfa52274dd61e1643d2205169732f29114bc240b3": "kraken",
        "0x2910543af39aba0cd09dbb2d50200b3e800a63d2": "kraken",
        "0xdc76cd25977e0a5ae17155770273ad58648900d3": "huobi",
        "0xab5c66752a9e8167967685f1450532fb96d5d24f": "huobi",
        "0x6748f50f686bfbca6fe8ad62b22228b87f31ff2b": "huobi",
        "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b": "okex",
        "0x236f9f97e0e62388479bf9e5ba4889e46b0273c3": "okex",
    }
    
    def __init__(self):
        self.api_key = settings.etherscan_api_key or ""
        self.client: Optional[httpx.AsyncClient] = None
        self._last_request_time = datetime.min
        self._request_interval = 0.25
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_ttl = 300  # 5 minutos
        
        if not self.api_key:
            logger.warning("Etherscan API key não configurada")
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Retorna cliente HTTP reutilizável."""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": "CryptoPulse/1.0"}
            )
        return self.client
    
    async def _rate_limit(self):
        """Aplica rate limiting."""
        now = datetime.now()
        elapsed = (now - self._last_request_time).total_seconds()
        if elapsed < self._request_interval:
            await asyncio.sleep(self._request_interval - elapsed)
        self._last_request_time = datetime.now()
    
    async def _make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Faz requisição à API V2."""
        if not self.api_key:
            return None
            
        await self._rate_limit()
        
        client = await self._get_client()
        params["chainid"] = self.CHAIN_ID
        params["apikey"] = self.api_key
        
        try:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            message = data.get("message", "")
            result = data.get("result", "")
            
            if status == "0":
                if "No transactions found" in str(result) or "No records found" in str(result):
                    return {"result": []}
                logger.debug(f"Etherscan: {message} - {result}")
                return None
            
            return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Etherscan HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Etherscan request error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Verifica se o coletor está disponível."""
        return bool(self.api_key)
    
    async def health_check(self) -> str:
        """Verifica se a API está acessível."""
        if not self.api_key:
            return "unavailable"
        
        try:
            params = {"module": "stats", "action": "ethprice"}
            result = await self._make_request(params)
            if result and result.get("status") == "1":
                return "healthy"
            return "degraded"
        except Exception:
            return "unhealthy"
    
    async def get_eth_price(self) -> float:
        """Obtém preço atual do ETH."""
        # Verificar cache de preço
        price_cache_key = "eth_price"
        if price_cache_key in self._cache:
            cache_time = self._cache_time.get(price_cache_key)
            if cache_time and (datetime.now() - cache_time).total_seconds() < 60:
                return float(self._cache[price_cache_key])
        
        if not self.api_key:
            return 3200.0
        
        params = {"module": "stats", "action": "ethprice"}
        result = await self._make_request(params)
        
        if result and result.get("status") == "1":
            eth_result = result.get("result", {})
            if isinstance(eth_result, dict):
                price = eth_result.get("ethusd")
                if price:
                    price_float = float(price)
                    self._cache[price_cache_key] = price_float
                    self._cache_time[price_cache_key] = datetime.now()
                    return price_float
        
        return 3200.0
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se o cache ainda é válido."""
        if cache_key not in self._cache_time:
            return False
        elapsed = (datetime.now() - self._cache_time[cache_key]).total_seconds()
        return elapsed < self._cache_ttl
    
    async def get_large_transactions(
        self,
        min_value_eth: Optional[float] = None,
        hours: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtém transações grandes de ETH."""
        # Usar padrões se não especificado
        actual_min_eth: float = min_value_eth if min_value_eth is not None else self.DEFAULT_MIN_ETH
        actual_hours: int = hours if hours is not None else self.DEFAULT_HOURS
        
        if not self.api_key:
            logger.warning("Etherscan requer API key gratuita")
            return []
        
        # Verificar cache
        cache_key = f"eth_txs_{actual_min_eth}_{actual_hours}"
        if self._is_cache_valid(cache_key) and cache_key in self._cache:
            logger.debug("Etherscan: usando cache")
            return self._cache[cache_key]
        
        transactions: List[Dict[str, Any]] = []
        eth_price = await self.get_eth_price()
        
        logger.info(f"Etherscan: coletando transações (min={actual_min_eth} ETH, price=${eth_price:.0f})")
        
        # Consultar endereços de exchange
        exchange_list = list(self.KNOWN_EXCHANGES.items())[:6]
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=actual_hours)
        
        for address, exchange_name in exchange_list:
            try:
                params = {
                    "module": "account",
                    "action": "txlist",
                    "address": address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "page": 1,
                    "offset": 50,
                    "sort": "desc",
                }
                
                result = await self._make_request(params)
                
                if not result:
                    continue
                
                tx_list = result.get("result", [])
                if not isinstance(tx_list, list):
                    continue
                
                for tx in tx_list:
                    try:
                        value_wei = int(tx.get("value", 0))
                        value_eth = value_wei / 1e18
                        value_usd = value_eth * eth_price
                        
                        if value_eth < actual_min_eth:
                            continue
                        
                        tx_timestamp = int(tx.get("timeStamp", 0))
                        tx_time = datetime.fromtimestamp(tx_timestamp, tz=timezone.utc)
                        
                        if tx_time < cutoff_time:
                            continue
                        
                        from_addr = tx.get("from", "").lower()
                        to_addr = tx.get("to", "").lower()
                        address_lower = address.lower()
                        
                        if from_addr == address_lower:
                            tx_type = "exchange_withdrawal"
                            from_owner = exchange_name
                            to_owner = self._identify_address(to_addr)
                        elif to_addr == address_lower:
                            tx_type = "exchange_deposit"
                            from_owner = self._identify_address(from_addr)
                            to_owner = exchange_name
                        else:
                            continue
                        
                        transactions.append({
                            "tx_hash": tx.get("hash"),
                            "blockchain": "ethereum",
                            "symbol": "ETH",
                            "amount": value_eth,
                            "amount_usd": value_usd,
                            "from_address": from_addr,
                            "from_owner": from_owner,
                            "to_address": to_addr,
                            "to_owner": to_owner,
                            "transaction_type": tx_type,
                            "timestamp": tx_time,
                            "block_number": int(tx.get("blockNumber", 0)),
                            "gas_used": int(tx.get("gasUsed", 0)),
                        })
                        
                    except (ValueError, KeyError, TypeError):
                        continue
                
            except Exception as e:
                logger.error(f"Erro {exchange_name}: {e}")
                continue
        
        # Remover duplicatas
        seen: set = set()
        unique_transactions: List[Dict[str, Any]] = []
        for tx in transactions:
            tx_hash = tx.get("tx_hash", "")
            if tx_hash and tx_hash not in seen:
                seen.add(tx_hash)
                unique_transactions.append(tx)
        
        unique_transactions.sort(key=lambda x: x["amount_usd"], reverse=True)
        result_list = unique_transactions[:limit]
        
        # Salvar no cache
        self._cache[cache_key] = result_list
        self._cache_time[cache_key] = datetime.now()
        
        logger.info(f"Etherscan: {len(result_list)} transações ETH coletadas")
        return result_list
    
    def _identify_address(self, address: str) -> str:
        """Identifica o dono de um endereço."""
        return self.KNOWN_EXCHANGES.get(address.lower(), "unknown")
    
    async def get_whale_stats(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """Calcula estatísticas de atividade de baleias."""
        actual_hours: int = hours if hours is not None else self.DEFAULT_HOURS
        
        # Usar mesmos parâmetros para aproveitar cache
        transactions = await self.get_large_transactions(
            min_value_eth=self.DEFAULT_MIN_ETH,
            hours=actual_hours,
            limit=200
        )
        
        if not transactions:
            return {
                "total_transactions": 0,
                "total_volume_usd": 0.0,
                "exchange_inflow_usd": 0.0,
                "exchange_outflow_usd": 0.0,
                "netflow_usd": 0.0,
                "largest_transaction_usd": 0.0,
            }
        
        total_volume = sum(tx["amount_usd"] for tx in transactions)
        inflow = sum(
            tx["amount_usd"] for tx in transactions 
            if tx["transaction_type"] == "exchange_deposit"
        )
        outflow = sum(
            tx["amount_usd"] for tx in transactions 
            if tx["transaction_type"] == "exchange_withdrawal"
        )
        largest = max(tx["amount_usd"] for tx in transactions)
        
        return {
            "total_transactions": len(transactions),
            "total_volume_usd": total_volume,
            "exchange_inflow_usd": inflow,
            "exchange_outflow_usd": outflow,
            "netflow_usd": inflow - outflow,
            "largest_transaction_usd": largest,
        }
    
    async def close(self):
        """Fecha o cliente HTTP."""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
