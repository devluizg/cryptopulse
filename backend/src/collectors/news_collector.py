"""
News Collector - Coleta notícias e eventos.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import hashlib

from loguru import logger

from src.collectors.base_collector import BaseCollector, APIError
from src.config.settings import settings


class NewsSentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class NewsImportance(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class NewsItem:
    id: str
    title: str
    url: str
    source: str
    symbols: List[str] = field(default_factory=list)
    sentiment: NewsSentiment = NewsSentiment.NEUTRAL
    importance: NewsImportance = NewsImportance.MEDIUM
    votes_positive: int = 0
    votes_negative: int = 0
    votes_important: int = 0
    published_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_significant(self) -> bool:
        return self.importance == NewsImportance.HIGH or self.votes_important > 5
    
    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "source": self.source, "sentiment": self.sentiment.value}


class CryptoPanicCollector(BaseCollector[NewsItem]):
    """Coletor de notícias do CryptoPanic."""
    
    BASE_URL = "https://cryptopanic.com/api/v1"
    
    def __init__(self):
        api_key = settings.cryptopanic_api_key
        if not api_key:
            logger.warning("CryptoPanic API key não configurada")
        
        super().__init__(name="cryptopanic", base_url=self.BASE_URL, api_key=api_key, rate_limit_delay=1.0)
    
    def _generate_id(self, title: str, source: str) -> str:
        return hashlib.md5(f"{title}:{source}".encode()).hexdigest()[:16]
    
    async def collect(self, symbols: Optional[List[str]] = None, hours: int = 24) -> List[NewsItem]:
        if not self.api_key:
            return []
        
        params: Dict[str, Any] = {"auth_token": self.api_key, "filter": "hot", "public": "true"}
        if symbols:
            params["currencies"] = ",".join(symbols)
        
        try:
            response = await self.get("posts/", params=params)
            results: List[NewsItem] = []
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            items = response.get("results", []) if isinstance(response, dict) else []
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                published_str = item.get("published_at", "")
                try:
                    published = datetime.fromisoformat(published_str.replace("Z", "+00:00")).replace(tzinfo=None)
                except:
                    published = datetime.utcnow()
                
                if published < cutoff:
                    continue
                
                source_info = item.get("source", {})
                source_name = source_info.get("title", "unknown") if isinstance(source_info, dict) else "unknown"
                
                currencies = item.get("currencies", [])
                item_symbols = [c.get("code", "").upper() for c in currencies if isinstance(c, dict) and c.get("code")]
                
                votes = item.get("votes", {}) or {}
                
                news = NewsItem(
                    id=self._generate_id(item.get("title", ""), source_name),
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    source=source_name,
                    symbols=item_symbols,
                    votes_positive=int(votes.get("positive", 0) or 0),
                    votes_negative=int(votes.get("negative", 0) or 0),
                    votes_important=int(votes.get("important", 0) or 0),
                    published_at=published,
                )
                results.append(news)
            
            return results
        except APIError as e:
            self.logger.error(f"Erro CryptoPanic: {e}")
            return []
    
    async def collect_single(self, symbol: str) -> Optional[NewsItem]:
        news = await self.collect(symbols=[symbol], hours=24)
        return news[0] if news else None
    
    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "unavailable", "collector": self.name}
        try:
            await self.get("posts/", params={"auth_token": self.api_key, "filter": "hot", "public": "true"})
            return {"status": "healthy", "collector": self.name}
        except:
            return {"status": "unhealthy", "collector": self.name}


class NewsCollector:
    """Agregador de coletores de notícias."""
    
    def __init__(self):
        self.cryptopanic = CryptoPanicCollector()
        self.logger = logger.bind(collector="news_aggregator")
    
    async def close(self):
        await self.cryptopanic.close()
    
    async def collect(self, symbols: Optional[List[str]] = None, hours: int = 24, include_rss: bool = True) -> List[NewsItem]:
        return await self.cryptopanic.collect(symbols, hours)
    
    async def get_narrative_score(self, symbol: str, hours: int = 24) -> float:
        news = await self.collect(symbols=[symbol], hours=hours)
        if not news:
            return 50.0
        return min(max(len(news) * 5 + 30, 0), 100)
    
    async def get_news_summary(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        news = await self.collect(symbols=[symbol], hours=hours)
        return {
            "symbol": symbol,
            "total_news": len(news),
            "positive_count": sum(1 for n in news if n.sentiment == NewsSentiment.POSITIVE),
            "negative_count": sum(1 for n in news if n.sentiment == NewsSentiment.NEGATIVE),
            "important_count": sum(1 for n in news if n.is_significant),
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        return {"cryptopanic": self.cryptopanic.get_metrics()}
    
    async def health_check(self) -> Dict[str, Any]:
        h = await self.cryptopanic.health_check()
        return {"status": h["status"], "sources": {"cryptopanic": h}}
