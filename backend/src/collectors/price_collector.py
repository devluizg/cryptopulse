"""
Price Collector - Coleta dados de preço de múltiplas fontes.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from loguru import logger

from src.collectors.base_collector import BaseCollector, APIError, CollectorError
from src.config.settings import settings


@dataclass
class PriceDataPoint:
    symbol: str
    price_usd: float
    price_btc: Optional[float] = None
    volume_24h: float = 0.0
    price_change_1h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_7d: Optional[float] = None
    market_cap: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    open_24h: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price_usd": self.price_usd,
            "volume_24h": self.volume_24h,
            "price_change_24h": self.price_change_24h,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


@dataclass
class OHLCVData:
    symbol: str
    timestamp: datetime
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str = "unknown"


class BinanceCollector(BaseCollector[PriceDataPoint]):
    """Coletor de preços da Binance."""
    
    BASE_URL = "https://api.binance.com"
    DEFAULT_RATE_LIMIT_DELAY = 0.1
    
    SYMBOL_MAP = {
        "BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT",
        "BNB": "BNBUSDT", "XRP": "XRPUSDT", "ADA": "ADAUSDT",
        "DOGE": "DOGEUSDT", "AVAX": "AVAXUSDT", "LINK": "LINKUSDT",
        "MATIC": "MATICUSDT", "DOT": "DOTUSDT", "UNI": "UNIUSDT",
    }
    
    TIMEFRAME_MAP = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
    
    def __init__(self):
        super().__init__(
            name="binance",
            base_url=self.BASE_URL,
            api_key=settings.binance_api_key,
            rate_limit_delay=self.DEFAULT_RATE_LIMIT_DELAY,
        )
    
    def _get_binance_symbol(self, symbol: str) -> Optional[str]:
        return self.SYMBOL_MAP.get(symbol.upper())
    
    async def collect(self, symbols: Optional[List[str]] = None) -> List[PriceDataPoint]:
        if symbols is None:
            symbols = list(self.SYMBOL_MAP.keys())
        
        self.logger.info(f"Coletando preços de {len(symbols)} símbolos da Binance")
        results: List[PriceDataPoint] = []
        
        try:
            response = await self.get("api/v3/ticker/24hr")
            
            # response é uma lista de dicts
            if isinstance(response, list):
                ticker_map: Dict[str, Dict[str, Any]] = {}
                for item in response:
                    if isinstance(item, dict):
                        ticker_map[item.get("symbol", "")] = item
                
                for symbol in symbols:
                    binance_symbol = self._get_binance_symbol(symbol)
                    if binance_symbol and binance_symbol in ticker_map:
                        ticker = ticker_map[binance_symbol]
                        price_data = self._parse_ticker(symbol, ticker)
                        results.append(price_data)
            
            self.logger.info(f"Coletados {len(results)} preços da Binance")
            
        except APIError as e:
            self.logger.error(f"Erro ao coletar da Binance: {e}")
            raise
        
        return results
    
    async def collect_single(self, symbol: str) -> Optional[PriceDataPoint]:
        binance_symbol = self._get_binance_symbol(symbol)
        if not binance_symbol:
            return None
        
        try:
            response = await self.get("api/v3/ticker/24hr", params={"symbol": binance_symbol})
            if isinstance(response, dict):
                return self._parse_ticker(symbol, response)
            return None
        except APIError as e:
            self.logger.error(f"Erro ao coletar {symbol}: {e}")
            return None
    
    def _parse_ticker(self, symbol: str, ticker: Dict[str, Any]) -> PriceDataPoint:
        return PriceDataPoint(
            symbol=symbol,
            price_usd=float(ticker.get("lastPrice", 0)),
            volume_24h=float(ticker.get("quoteVolume", 0)),
            price_change_24h=float(ticker.get("priceChangePercent", 0)),
            high_24h=float(ticker.get("highPrice", 0)),
            low_24h=float(ticker.get("lowPrice", 0)),
            open_24h=float(ticker.get("openPrice", 0)),
            timestamp=datetime.utcnow(),
            source="binance",
        )
    
    async def get_klines(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> List[OHLCVData]:
        binance_symbol = self._get_binance_symbol(symbol)
        if not binance_symbol:
            return []
        
        interval = self.TIMEFRAME_MAP.get(timeframe)
        if not interval:
            return []
        
        try:
            response = await self.get("api/v3/klines", params={
                "symbol": binance_symbol,
                "interval": interval,
                "limit": min(limit, 1000),
            })
            
            results: List[OHLCVData] = []
            if isinstance(response, list):
                for k in response:
                    if isinstance(k, list) and len(k) >= 6:
                        ohlcv = OHLCVData(
                            symbol=symbol,
                            timestamp=datetime.utcfromtimestamp(int(k[0]) / 1000),
                            timeframe=timeframe,
                            open=float(k[1]),
                            high=float(k[2]),
                            low=float(k[3]),
                            close=float(k[4]),
                            volume=float(k[5]),
                            source="binance",
                        )
                        results.append(ohlcv)
            
            return results
        except APIError as e:
            self.logger.error(f"Erro ao coletar klines: {e}")
            return []
    
    async def get_volume_history(self, symbol: str, days: int = 30) -> List[float]:
        klines = await self.get_klines(symbol, timeframe="1d", limit=days)
        return [k.volume for k in klines]
    
    async def health_check(self) -> Dict[str, Any]:
        try:
            await self.get("api/v3/ping")
            return {"status": "healthy", "collector": self.name}
        except Exception as e:
            return {"status": "unhealthy", "collector": self.name, "error": str(e)}


class CoinGeckoCollector(BaseCollector[PriceDataPoint]):
    """Coletor de preços do CoinGecko."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    DEFAULT_RATE_LIMIT_DELAY = 1.5
    
    COINGECKO_IDS = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
        "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
        "DOGE": "dogecoin", "AVAX": "avalanche-2", "LINK": "chainlink",
        "MATIC": "matic-network", "DOT": "polkadot", "UNI": "uniswap",
    }
    
    def __init__(self):
        api_key = settings.coingecko_api_key
        base_url = self.BASE_URL
        if api_key:
            base_url = "https://pro-api.coingecko.com/api/v3"
        
        super().__init__(
            name="coingecko",
            base_url=base_url,
            api_key=api_key,
            rate_limit_delay=self.DEFAULT_RATE_LIMIT_DELAY,
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        headers = super()._get_default_headers()
        if self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key
        return headers
    
    def _get_coingecko_id(self, symbol: str) -> Optional[str]:
        return self.COINGECKO_IDS.get(symbol.upper())
    
    async def collect(self, symbols: Optional[List[str]] = None) -> List[PriceDataPoint]:
        if symbols is None:
            symbols = list(self.COINGECKO_IDS.keys())
        
        cg_ids = []
        symbol_map: Dict[str, str] = {}
        for s in symbols:
            cg_id = self._get_coingecko_id(s)
            if cg_id:
                cg_ids.append(cg_id)
                symbol_map[cg_id] = s
        
        if not cg_ids:
            return []
        
        try:
            response = await self.get("coins/markets", params={
                "vs_currency": "usd",
                "ids": ",".join(cg_ids),
                "order": "market_cap_desc",
                "sparkline": "false",
            })
            
            results: List[PriceDataPoint] = []
            if isinstance(response, list):
                for coin in response:
                    if isinstance(coin, dict):
                        coin_id = coin.get("id", "")
                        symbol = symbol_map.get(coin_id)
                        if symbol:
                            results.append(self._parse_market_data(symbol, coin))
            
            return results
            
        except APIError as e:
            self.logger.error(f"Erro ao coletar do CoinGecko: {e}")
            raise
    
    async def collect_single(self, symbol: str) -> Optional[PriceDataPoint]:
        results = await self.collect([symbol])
        return results[0] if results else None
    
    def _parse_market_data(self, symbol: str, data: Dict[str, Any]) -> PriceDataPoint:
        return PriceDataPoint(
            symbol=symbol,
            price_usd=float(data.get("current_price", 0) or 0),
            volume_24h=float(data.get("total_volume", 0) or 0),
            price_change_24h=float(data.get("price_change_percentage_24h", 0) or 0),
            market_cap=float(data.get("market_cap", 0) or 0),
            high_24h=float(data.get("high_24h", 0) or 0),
            low_24h=float(data.get("low_24h", 0) or 0),
            timestamp=datetime.utcnow(),
            source="coingecko",
        )
    
    async def health_check(self) -> Dict[str, Any]:
        try:
            result = await self.get("ping")
            return {"status": "healthy", "collector": self.name}
        except Exception as e:
            return {"status": "unhealthy", "collector": self.name, "error": str(e)}


class PriceCollector:
    """Agregador de coletores de preço."""
    
    def __init__(self):
        self.binance = BinanceCollector()
        self.coingecko = CoinGeckoCollector()
        self.logger = logger.bind(collector="price_aggregator")
    
    async def close(self):
        await self.binance.close()
        await self.coingecko.close()
    
    async def collect(self, symbols: Optional[List[str]] = None) -> List[PriceDataPoint]:
        try:
            results = await self.binance.collect(symbols)
            if results:
                return results
        except CollectorError:
            pass
        
        try:
            return await self.coingecko.collect(symbols)
        except CollectorError:
            return []
    
    async def collect_single(self, symbol: str) -> Optional[PriceDataPoint]:
        result = await self.binance.collect_single(symbol)
        if result:
            return result
        return await self.coingecko.collect_single(symbol)
    
    async def get_klines(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> List[OHLCVData]:
        return await self.binance.get_klines(symbol, timeframe, limit)
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "binance": self.binance.get_metrics(),
            "coingecko": self.coingecko.get_metrics(),
        }
    
    async def health_check(self) -> Dict[str, Any]:
        b_health = await self.binance.health_check()
        c_health = await self.coingecko.health_check()
        return {
            "status": "healthy" if b_health["status"] == "healthy" or c_health["status"] == "healthy" else "unhealthy",
            "sources": {"binance": b_health, "coingecko": c_health}
        }
