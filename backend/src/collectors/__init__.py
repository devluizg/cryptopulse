"""
CryptoPulse Collectors - Módulo de coleta de dados.
"""

from src.collectors.base_collector import (
    BaseCollector,
    CollectorError,
    RateLimitError,
    APIError,
    CollectorMetrics,
)

from src.collectors.price_collector import (
    PriceCollector,
    BinanceCollector,
    CoinGeckoCollector,
    PriceDataPoint,
    OHLCVData,
)

from src.collectors.whale_collector import (
    WhaleCollector,
    WhaleAlertCollector,
    WhaleTransaction,
    TransactionType,
)

from src.collectors.exchange_flow_collector import (
    ExchangeFlowCollector,
    ExchangeFlowData,
)

from src.collectors.news_collector import (
    NewsCollector,
    CryptoPanicCollector,
    NewsItem,
    NewsSentiment,
    NewsImportance,
)

from src.collectors.oi_collector import (
    OpenInterestCollector,
    BinanceFuturesCollector,
    OpenInterestData,
)

from src.collectors.collector_manager import (
    CollectorManager,
    get_collector_manager,
    close_collector_manager,
)

__all__ = [
    "BaseCollector", "CollectorError", "RateLimitError", "APIError", "CollectorMetrics",
    "PriceCollector", "BinanceCollector", "CoinGeckoCollector", "PriceDataPoint", "OHLCVData",
    "WhaleCollector", "WhaleAlertCollector", "WhaleTransaction", "TransactionType",
    "ExchangeFlowCollector", "ExchangeFlowData",
    "NewsCollector", "CryptoPanicCollector", "NewsItem", "NewsSentiment", "NewsImportance",
    "OpenInterestCollector", "BinanceFuturesCollector", "OpenInterestData",
    "CollectorManager", "get_collector_manager", "close_collector_manager",
]
