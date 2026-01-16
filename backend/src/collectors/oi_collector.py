"""
Open Interest Collector.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from loguru import logger

from src.collectors.base_collector import BaseCollector, APIError
from src.config.settings import settings


@dataclass
class OpenInterestData:
    symbol: str
    open_interest: float
    open_interest_usd: float
    funding_rate: Optional[float] = None
    long_short_ratio: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "unknown"


class BinanceFuturesCollector(BaseCollector[OpenInterestData]):
    """Coletor de Open Interest da Binance Futures."""
    
    BASE_URL = "https://fapi.binance.com"
    
    SYMBOL_MAP = {
        "BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT",
        "BNB": "BNBUSDT", "XRP": "XRPUSDT", "ADA": "ADAUSDT",
        "DOGE": "DOGEUSDT", "AVAX": "AVAXUSDT", "LINK": "LINKUSDT",
    }
    
    def __init__(self):
        super().__init__(
            name="binance_futures",
            base_url=self.BASE_URL,
            api_key=settings.binance_api_key,
            rate_limit_delay=0.1,
        )
    
    def _get_futures_symbol(self, symbol: str) -> Optional[str]:
        return self.SYMBOL_MAP.get(symbol.upper())
    
    async def collect(self, symbols: Optional[List[str]] = None) -> List[OpenInterestData]:
        if symbols is None:
            symbols = list(self.SYMBOL_MAP.keys())
        
        results: List[OpenInterestData] = []
        for symbol in symbols:
            data = await self.collect_single(symbol)
            if data:
                results.append(data)
        return results
    
    async def collect_single(self, symbol: str) -> Optional[OpenInterestData]:
        futures_symbol = self._get_futures_symbol(symbol)
        if not futures_symbol:
            return None
        
        try:
            oi_resp = await self.get("fapi/v1/openInterest", params={"symbol": futures_symbol})
            oi = float(oi_resp.get("openInterest", 0)) if isinstance(oi_resp, dict) else 0
            
            price_resp = await self.get("fapi/v1/ticker/price", params={"symbol": futures_symbol})
            price = float(price_resp.get("price", 0)) if isinstance(price_resp, dict) else 0
            
            funding_rate = None
            try:
                fr_resp = await self.get("fapi/v1/fundingRate", params={"symbol": futures_symbol, "limit": 1})
                if isinstance(fr_resp, list) and len(fr_resp) > 0:
                    first_item: Any = list(fr_resp)[0]
                    if isinstance(first_item, dict):
                        fr_value = first_item.get("fundingRate", 0)
                        funding_rate = float(fr_value) * 100 if fr_value else None
            except Exception:
                pass
            
            return OpenInterestData(
                symbol=symbol,
                open_interest=oi,
                open_interest_usd=oi * price,
                funding_rate=funding_rate,
                timestamp=datetime.utcnow(),
                source="binance_futures",
            )
        except APIError as e:
            self.logger.error(f"Erro OI {symbol}: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        try:
            await self.get("fapi/v1/ping")
            return {"status": "healthy", "collector": self.name}
        except Exception:
            return {"status": "unhealthy", "collector": self.name}


class OpenInterestCollector:
    """Agregador de coletores de OI."""
    
    def __init__(self):
        self.binance_futures = BinanceFuturesCollector()
        self.logger = logger.bind(collector="oi_aggregator")
    
    async def close(self):
        await self.binance_futures.close()
    
    async def collect(self, symbols: Optional[List[str]] = None) -> List[OpenInterestData]:
        return await self.binance_futures.collect(symbols)
    
    async def collect_single(self, symbol: str) -> Optional[OpenInterestData]:
        return await self.binance_futures.collect_single(symbol)
    
    async def get_oi_pressure_score(self, symbol: str) -> Optional[float]:
        data = await self.collect_single(symbol)
        if not data:
            return None
        score = 50.0
        if data.funding_rate:
            score += data.funding_rate * 100
        return min(max(score, 0), 100)
    
    def get_metrics(self) -> Dict[str, Any]:
        return {"binance_futures": self.binance_futures.get_metrics()}
    
    async def health_check(self) -> Dict[str, Any]:
        h = await self.binance_futures.health_check()
        return {"status": h["status"], "sources": {"binance_futures": h}}
