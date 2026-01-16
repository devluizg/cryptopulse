"""
Exchange Flow Collector - Coleta dados de fluxo de exchanges.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from loguru import logger

from src.collectors.base_collector import BaseCollector, APIError
from src.config.api_keys import api_keys


@dataclass
class ExchangeFlowData:
    symbol: str
    exchange: Optional[str] = None
    inflow: float = 0.0
    inflow_usd: float = 0.0
    outflow: float = 0.0
    outflow_usd: float = 0.0
    netflow: float = 0.0
    netflow_usd: float = 0.0
    reserve: Optional[float] = None
    reserve_change_24h: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    timeframe: str = "24h"
    source: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol, "exchange": self.exchange,
            "inflow": self.inflow, "outflow": self.outflow,
            "netflow": self.netflow, "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


class ExchangeFlowCollector:
    """Agregador de coletores de fluxo de exchanges."""
    
    def __init__(self):
        self.logger = logger.bind(collector="exchange_flow_aggregator")
        self._cache: Dict[str, ExchangeFlowData] = {}
        self._cache_times: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)
    
    async def close(self):
        pass
    
    async def collect(self, symbols: Optional[List[str]] = None, use_cache: bool = True) -> List[ExchangeFlowData]:
        # Sem API keys de CryptoQuant/Glassnode, retornamos lista vazia
        self.logger.warning("Exchange flow collectors requerem API keys (CryptoQuant/Glassnode)")
        return []
    
    async def collect_single(self, symbol: str) -> Optional[ExchangeFlowData]:
        return None
    
    async def get_netflow_score(self, symbol: str) -> Optional[float]:
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        return {"cache_size": len(self._cache)}
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "unavailable", "sources": {}}
