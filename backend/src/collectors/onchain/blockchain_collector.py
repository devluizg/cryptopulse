"""
CryptoPulse - Blockchain.com Collector
Coleta transações grandes de BTC usando a API gratuita do Blockchain.com

NOTA: A API gratuita tem rate limit muito restritivo.
Estratégia: Usar cache e reduzir número de requests.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

import httpx

from src.utils.logger import logger


class BlockchainCollector:
    """
    Coletor de transações grandes de Bitcoin via Blockchain.com API.
    
    API Gratuita - LIMITAÇÕES:
    - Rate limit muito restritivo (~1 request a cada 10-15 segundos)
    - Sem API key disponível para aumentar limite
    
    Estratégia para contornar:
    - Usar apenas 2-3 endereços de exchange por coleta
    - Cache de resultados por 10 minutos
    - Intervalo maior entre requests (15s)
    """
    
    BASE_URL = "https://blockchain.info"
    
    # Endereços mais ativos das principais exchanges (reduzido para evitar rate limit)
    KNOWN_EXCHANGES: Dict[str, str] = {
        "bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h": "binance",
        "3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb": "binance",
        "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh": "binance",
    }
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self._last_request_time = datetime.min
        self._request_interval = 15.0  # 15 segundos entre requests
        self._cache: Dict[str, Any] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 600  # Cache válido por 10 minutos
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Retorna cliente HTTP reutilizável."""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
        return self.client
    
    async def _rate_limit(self):
        """Aplica rate limiting conservador."""
        now = datetime.now()
        elapsed = (now - self._last_request_time).total_seconds()
        if elapsed < self._request_interval:
            wait_time = self._request_interval - elapsed
            logger.debug(f"Blockchain.com: aguardando {wait_time:.1f}s (rate limit)")
            await asyncio.sleep(wait_time)
        self._last_request_time = datetime.now()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Faz requisição à API com rate limiting conservador."""
        await self._rate_limit()
        
        client = await self._get_client()
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = await client.get(url, params=params or {})
            
            if response.status_code == 429:
                logger.warning("Blockchain.com rate limit - usando cache se disponível")
                return None
            
            if response.status_code == 403:
                logger.warning("Blockchain.com bloqueou request (403)")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Blockchain.com HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Blockchain.com request error: {e}")
            return None
    
    async def health_check(self) -> str:
        """Verifica se a API está acessível."""
        try:
            result = await self._make_request("ticker")
            if result and "USD" in result:
                return "healthy"
            return "degraded"
        except Exception:
            return "unhealthy"
    
    async def get_btc_price(self) -> Optional[float]:
        """Obtém preço atual do BTC."""
        result = await self._make_request("ticker")
        if result and "USD" in result:
            return float(result["USD"].get("last", 0))
        return 95000.0  # Fallback
    
    def _is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido."""
        if not self._cache_time:
            return False
        elapsed = (datetime.now() - self._cache_time).total_seconds()
        return elapsed < self._cache_ttl
    
    async def get_large_transactions(
        self,
        min_value_btc: float = 10.0,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtém transações grandes de BTC.
        
        Devido ao rate limit restritivo, usa cache agressivo.
        """
        # Verificar cache
        cache_key = f"btc_txs_{min_value_btc}_{hours}"
        if self._is_cache_valid() and cache_key in self._cache:
            logger.debug("Blockchain.com: usando cache")
            return self._cache[cache_key]
        
        transactions: List[Dict[str, Any]] = []
        btc_price = await self.get_btc_price() or 95000.0
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Usar apenas 2 exchanges para reduzir requests
        exchange_list = list(self.KNOWN_EXCHANGES.items())[:2]
        
        for address, exchange_name in exchange_list:
            try:
                # Endpoint mais leve: últimos unspent outputs
                result = await self._make_request(f"rawaddr/{address}", {"limit": 20})
                
                if not result or "txs" not in result:
                    logger.debug(f"Sem dados para {exchange_name}")
                    continue
                
                for tx in result.get("txs", [])[:10]:  # Limitar processamento
                    try:
                        tx_time = datetime.fromtimestamp(
                            tx.get("time", 0),
                            tz=timezone.utc
                        )
                        if tx_time < cutoff_time:
                            continue
                        
                        # Calcular valor total
                        total_output_satoshi = sum(
                            out.get("value", 0) for out in tx.get("out", [])
                        )
                        value_btc = total_output_satoshi / 1e8
                        value_usd = value_btc * btc_price
                        
                        if value_btc < min_value_btc:
                            continue
                        
                        # Determinar tipo de transação
                        input_addresses = [
                            inp.get("prev_out", {}).get("addr", "")
                            for inp in tx.get("inputs", [])
                            if inp.get("prev_out", {}).get("addr")
                        ]
                        
                        output_addresses = [
                            out.get("addr") for out in tx.get("out", [])
                            if out.get("addr")
                        ]
                        
                        if address in input_addresses:
                            tx_type = "exchange_withdrawal"
                            from_owner = exchange_name
                            to_owner = "unknown"
                        elif address in output_addresses:
                            tx_type = "exchange_deposit"
                            from_owner = "unknown"
                            to_owner = exchange_name
                        else:
                            continue
                        
                        transactions.append({
                            "tx_hash": tx.get("hash"),
                            "blockchain": "bitcoin",
                            "symbol": "BTC",
                            "amount": value_btc,
                            "amount_usd": value_usd,
                            "from_address": input_addresses[0] if input_addresses else "",
                            "from_owner": from_owner,
                            "to_address": output_addresses[0] if output_addresses else "",
                            "to_owner": to_owner,
                            "transaction_type": tx_type,
                            "timestamp": tx_time,
                            "block_height": tx.get("block_height", 0),
                        })
                        
                    except (ValueError, KeyError, TypeError) as e:
                        logger.debug(f"Erro ao processar tx: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Erro ao buscar transações de {exchange_name}: {e}")
                continue
        
        # Remover duplicatas e ordenar
        seen: set = set()
        unique_transactions: List[Dict[str, Any]] = []
        for tx in transactions:
            tx_hash = tx.get("tx_hash", "")
            if tx_hash and tx_hash not in seen:
                seen.add(tx_hash)
                unique_transactions.append(tx)
        
        unique_transactions.sort(key=lambda x: x["amount_usd"], reverse=True)
        result = unique_transactions[:limit]
        
        # Salvar no cache
        self._cache[cache_key] = result
        self._cache_time = datetime.now()
        
        logger.info(f"Blockchain.com: {len(result)} transações BTC coletadas")
        return result
    
    async def get_whale_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Calcula estatísticas de atividade de baleias BTC."""
        transactions = await self.get_large_transactions(
            min_value_btc=10.0,
            hours=hours,
            limit=50
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
        largest = max(tx["amount_usd"] for tx in transactions) if transactions else 0
        
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
