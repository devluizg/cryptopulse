"""
Collector Manager - Orquestrador central.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import asyncio

from loguru import logger

from src.collectors.price_collector import PriceCollector, PriceDataPoint, OHLCVData
from src.collectors.whale_collector import WhaleCollector, WhaleTransaction
from src.collectors.exchange_flow_collector import ExchangeFlowCollector, ExchangeFlowData
from src.collectors.news_collector import NewsCollector, NewsItem
from src.collectors.oi_collector import OpenInterestCollector, OpenInterestData


class CollectorManager:
    def __init__(self):
        self.price_collector = PriceCollector()
        self.whale_collector = WhaleCollector()
        self.exchange_flow_collector = ExchangeFlowCollector()
        self.news_collector = NewsCollector()
        self.oi_collector = OpenInterestCollector()
        self.logger = logger.bind(component="collector_manager")
        self._initialized = False
        self._cache: Dict[str, Any] = {}
        self._cache_times: Dict[str, datetime] = {}
    
    async def initialize(self):
        if self._initialized:
            return
        self.logger.info("Inicializando Collector Manager...")
        self._initialized = True
    
    async def close(self):
        await self.price_collector.close()
        await self.whale_collector.close()
        await self.exchange_flow_collector.close()
        await self.news_collector.close()
        await self.oi_collector.close()
        self._initialized = False
    
    async def collect_all(self, symbols: Optional[List[str]] = None, include_news: bool = True) -> Dict[str, Any]:
        start = datetime.utcnow()
        errors: List[str] = []
        
        prices: List[PriceDataPoint] = []
        whales: List[WhaleTransaction] = []
        flows: List[ExchangeFlowData] = []
        oi: List[OpenInterestData] = []
        news: List[NewsItem] = []
        
        try:
            prices = await self.price_collector.collect(symbols)
        except Exception as e:
            errors.append(f"prices: {e}")
        
        try:
            whales = await self.whale_collector.collect(symbols)
        except Exception as e:
            errors.append(f"whales: {e}")
        
        try:
            flows = await self.exchange_flow_collector.collect(symbols)
        except Exception as e:
            errors.append(f"flows: {e}")
        
        try:
            oi = await self.oi_collector.collect(symbols)
        except Exception as e:
            errors.append(f"oi: {e}")
        
        if include_news:
            try:
                news = await self.news_collector.collect(symbols)
            except Exception as e:
                errors.append(f"news: {e}")
        
        elapsed = (datetime.utcnow() - start).total_seconds()
        
        return {
            "prices": prices,
            "whales": whales,
            "exchange_flows": flows,
            "open_interest": oi,
            "news": news,
            "collected_at": datetime.utcnow(),
            "symbols": symbols or [],
            "errors": errors,
            "elapsed_seconds": elapsed,
        }
    
    async def collect_prices(self, symbols: Optional[List[str]] = None, use_cache: bool = False) -> List[PriceDataPoint]:
        return await self.price_collector.collect(symbols)
    
    async def collect_whales(self, symbols: Optional[List[str]] = None, use_cache: bool = False, min_usd: float = 500000, hours: int = 24) -> List[WhaleTransaction]:
        return await self.whale_collector.collect(symbols, min_usd, hours)
    
    async def collect_exchange_flows(self, symbols: Optional[List[str]] = None, use_cache: bool = False) -> List[ExchangeFlowData]:
        return await self.exchange_flow_collector.collect(symbols)
    
    async def collect_news(self, symbols: Optional[List[str]] = None, use_cache: bool = False, hours: int = 24) -> List[NewsItem]:
        return await self.news_collector.collect(symbols, hours)
    
    async def collect_open_interest(self, symbols: Optional[List[str]] = None, use_cache: bool = False) -> List[OpenInterestData]:
        return await self.oi_collector.collect(symbols)
    
    async def collect_for_symbol(self, symbol: str, include_news: bool = True) -> Dict[str, Any]:
        price = await self.price_collector.collect_single(symbol)
        whales = await self.whale_collector.collect([symbol])
        flow = await self.exchange_flow_collector.collect_single(symbol)
        oi = await self.oi_collector.collect_single(symbol)
        news = await self.news_collector.collect([symbol]) if include_news else []
        
        return {
            "symbol": symbol,
            "price": price,
            "whales": whales,
            "exchange_flow": flow,
            "open_interest": oi,
            "news": news,
            "collected_at": datetime.utcnow(),
        }
    
    async def get_klines(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> List[OHLCVData]:
        return await self.price_collector.get_klines(symbol, timeframe, limit)
    
    async def get_volume_history(self, symbol: str, days: int = 30) -> List[float]:
        return await self.price_collector.binance.get_volume_history(symbol, days)
    
    async def get_whale_stats(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        return await self.whale_collector.get_stats_by_symbol(symbol, hours)
    
    async def get_narrative_score(self, symbol: str, hours: int = 24) -> Optional[float]:
        return await self.news_collector.get_narrative_score(symbol, hours)
    
    async def get_oi_pressure_score(self, symbol: str) -> Optional[float]:
        return await self.oi_collector.get_oi_pressure_score(symbol)
    
    async def get_netflow_score(self, symbol: str) -> Optional[float]:
        return await self.exchange_flow_collector.get_netflow_score(symbol)
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "price": self.price_collector.get_metrics(),
            "whale": self.whale_collector.get_metrics(),
            "exchange_flow": self.exchange_flow_collector.get_metrics(),
            "news": self.news_collector.get_metrics(),
            "open_interest": self.oi_collector.get_metrics(),
            "cache": {"entries": len(self._cache)},
        }
    
    async def health_check(self) -> Dict[str, Any]:
        p = await self.price_collector.health_check()
        w = await self.whale_collector.health_check()
        e = await self.exchange_flow_collector.health_check()
        n = await self.news_collector.health_check()
        o = await self.oi_collector.health_check()
        
        sources = {"price": p, "whale": w, "exchange_flow": e, "news": n, "open_interest": o}
        healthy = sum(1 for s in sources.values() if s.get("status") in ["healthy", "degraded"])
        
        return {
            "status": "healthy" if healthy >= 2 else "degraded" if healthy >= 1 else "unhealthy",
            "healthy_sources": healthy,
            "total_sources": len(sources),
            "sources": sources,
        }


_manager: Optional[CollectorManager] = None

async def get_collector_manager() -> CollectorManager:
    global _manager
    if _manager is None:
        _manager = CollectorManager()
        await _manager.initialize()
    return _manager

async def close_collector_manager():
    global _manager
    if _manager:
        await _manager.close()
        _manager = None
