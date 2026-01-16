"""
Data Collection Job - Job de coleta de dados.

Responsável por:
- Coletar preços de todas as criptos
- Coletar transações de whales
- Coletar notícias
- Coletar Open Interest
- Coletar Klines (candles OHLCV)
- Persistir dados no banco
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger

from src.jobs.base_job import BaseJob, JobResult
from src.config.jobs_config import (
    JobConfig,
    PRICE_COLLECTION_JOB,
    WHALE_COLLECTION_JOB,
    NEWS_COLLECTION_JOB,
    OI_COLLECTION_JOB,
    KLINE_COLLECTION_JOB,
)
from src.collectors.collector_manager import CollectorManager, get_collector_manager
from src.database.connection import async_session_maker
from src.database.repositories import (
    AssetRepository,
    PriceRepository,
    WhaleRepository,
)


class PriceCollectionJob(BaseJob):
    """
    Job de coleta de preços.
    
    Intervalo: 1 minuto
    Fontes: Binance, CoinGecko
    """
    
    def __init__(self, config: Optional[JobConfig] = None):
        super().__init__(config or PRICE_COLLECTION_JOB)
        self._collector_manager: Optional[CollectorManager] = None
    
    async def setup(self) -> None:
        """Inicializa o collector manager."""
        self._collector_manager = await get_collector_manager()
    
    async def execute(self) -> Dict[str, Any]:
        """
        Coleta preços de todos os ativos ativos.
        
        Returns:
            Dict com estatísticas da coleta
        """
        if not self._collector_manager:
            raise RuntimeError("CollectorManager não inicializado")
        
        stats = {
            "assets_processed": 0,
            "prices_collected": 0,
            "prices_saved": 0,
            "errors": [],
        }
        
        async with async_session_maker() as session:
            asset_repo = AssetRepository(session)
            price_repo = PriceRepository(session)
            
            # Busca ativos ativos
            assets = await asset_repo.get_active_assets()
            symbols = [a.symbol for a in assets]
            
            if not symbols:
                self.logger.warning("Nenhum ativo ativo encontrado")
                return stats
            
            self.logger.info(f"Coletando preços para {len(symbols)} ativos")
            stats["assets_processed"] = len(symbols)
            
            # Coleta preços
            try:
                prices = await self._collector_manager.collect_prices(symbols)
                stats["prices_collected"] = len(prices)
            except Exception as e:
                stats["errors"].append(f"Coleta: {str(e)}")
                self.logger.error(f"Erro na coleta de preços: {e}")
                prices = []
            
            # Mapeia symbol -> asset_id
            symbol_to_id = await asset_repo.get_symbol_id_map()
            
            # Salva preços (snapshot atual - timeframe 1m para dados em tempo real)
            for price_data in prices:
                try:
                    symbol = price_data.symbol
                    asset_id = symbol_to_id.get(symbol)
                    
                    if not asset_id:
                        continue
                    
                    await price_repo.upsert_price(
                        asset_id=asset_id,
                        timestamp=datetime.utcnow(),
                        timeframe="1m",
                        open_price=price_data.price_usd,
                        high_price=price_data.high_24h or price_data.price_usd,
                        low_price=price_data.low_24h or price_data.price_usd,
                        close_price=price_data.price_usd,
                        volume=price_data.volume_24h or 0,
                        source="binance",
                    )
                    stats["prices_saved"] += 1
                    
                except Exception as e:
                    stats["errors"].append(f"{price_data.symbol}: {str(e)}")
            
            await session.commit()
        
        self.logger.info(
            f"Preços coletados: {stats['prices_collected']}, "
            f"salvos: {stats['prices_saved']}"
        )
        
        return stats


class WhaleCollectionJob(BaseJob):
    """
    Job de coleta de transações de whales.
    
    Intervalo: 5 minutos
    Fontes: Etherscan (ETH), Blockchain.com (BTC)
    
    NOTA: Parâmetros ajustados para capturar mais transações com APIs gratuitas
    """
    
    # Configurações ajustadas para APIs gratuitas
    MIN_USD = 30_000        # $30k mínimo (captura mais transações)
    HOURS = 6               # Últimas 6 horas (evita reprocessar muito)
    
    def __init__(self, config: Optional[JobConfig] = None):
        super().__init__(config or WHALE_COLLECTION_JOB)
        self._collector_manager: Optional[CollectorManager] = None
    
    async def setup(self) -> None:
        """Inicializa o collector manager."""
        self._collector_manager = await get_collector_manager()
    
    async def execute(self) -> Dict[str, Any]:
        """
        Coleta transações de whales.
        
        Returns:
            Dict com estatísticas da coleta
        """
        if not self._collector_manager:
            raise RuntimeError("CollectorManager não inicializado")
        
        stats = {
            "transactions_collected": 0,
            "transactions_saved": 0,
            "new_transactions": 0,
            "duplicate_transactions": 0,
            "by_symbol": {},
            "errors": [],
        }
        
        async with async_session_maker() as session:
            asset_repo = AssetRepository(session)
            whale_repo = WhaleRepository(session)
            
            # BTC e ETH têm APIs gratuitas
            symbols = ["BTC", "ETH"]
            symbol_to_id = await asset_repo.get_symbol_id_map()
            
            self.logger.info(f"Coletando whales para: {symbols} (min=${self.MIN_USD:,}, hours={self.HOURS})")
            
            # Coleta transações
            try:
                transactions = await self._collector_manager.collect_whales(
                    symbols=symbols,
                    min_usd=self.MIN_USD,
                    hours=self.HOURS,
                )
                stats["transactions_collected"] = len(transactions)
            except Exception as e:
                stats["errors"].append(f"Coleta: {str(e)}")
                self.logger.error(f"Erro na coleta de whales: {e}")
                transactions = []
            
            # Salva transações
            for tx in transactions:
                try:
                    symbol = tx.symbol
                    asset_id = symbol_to_id.get(symbol)
                    
                    if not asset_id:
                        self.logger.debug(f"Asset não encontrado: {symbol}")
                        continue
                    
                    # Verifica se já existe (por hash)
                    if tx.tx_hash:
                        exists = await whale_repo.tx_exists(tx.tx_hash)
                        if exists:
                            stats["duplicate_transactions"] += 1
                            continue
                    
                    # Cria transação
                    await whale_repo.create_transaction(
                        asset_id=asset_id,
                        tx_hash=tx.tx_hash or f"auto_{datetime.utcnow().timestamp()}_{symbol}",
                        from_address=tx.from_address or "",
                        to_address=tx.to_address or "",
                        amount=tx.amount,
                        amount_usd=tx.amount_usd,
                        transaction_type=tx.transaction_type.value if hasattr(tx.transaction_type, 'value') else str(tx.transaction_type),
                        timestamp=tx.timestamp or datetime.utcnow(),
                        from_owner=tx.from_owner,
                        to_owner=tx.to_owner,
                        blockchain=tx.blockchain or "unknown",
                    )
                    
                    stats["transactions_saved"] += 1
                    stats["new_transactions"] += 1
                    
                    # Contagem por símbolo
                    if symbol not in stats["by_symbol"]:
                        stats["by_symbol"][symbol] = 0
                    stats["by_symbol"][symbol] += 1
                    
                except Exception as e:
                    tx_hash = getattr(tx, 'tx_hash', 'unknown')
                    stats["errors"].append(f"TX {tx_hash[:20]}...: {str(e)}")
                    self.logger.error(f"Erro salvando TX: {e}")
            
            await session.commit()
        
        self.logger.info(
            f"Whales: coletados={stats['transactions_collected']}, "
            f"novos={stats['new_transactions']}, "
            f"duplicados={stats['duplicate_transactions']}, "
            f"por_symbol={stats['by_symbol']}"
        )
        
        return stats


class NewsCollectionJob(BaseJob):
    """
    Job de coleta de notícias.
    
    Intervalo: 10 minutos
    Fontes: CryptoPanic
    """
    
    def __init__(self, config: Optional[JobConfig] = None):
        super().__init__(config or NEWS_COLLECTION_JOB)
        self._collector_manager: Optional[CollectorManager] = None
    
    async def setup(self) -> None:
        """Inicializa o collector manager."""
        self._collector_manager = await get_collector_manager()
    
    async def execute(self) -> Dict[str, Any]:
        """
        Coleta notícias recentes.
        
        Returns:
            Dict com estatísticas da coleta
        """
        if not self._collector_manager:
            raise RuntimeError("CollectorManager não inicializado")
        
        stats = {
            "news_collected": 0,
            "symbols_with_news": [],
            "avg_sentiment": 0.0,
            "errors": [],
        }
        
        try:
            news_list = await self._collector_manager.collect_news(
                symbols=None,
                hours=2,
            )
            stats["news_collected"] = len(news_list)
            
            if news_list:
                sentiments = []
                symbols_found = set()
                
                for news in news_list:
                    news_symbols = getattr(news, 'symbols', []) or []
                    for sym in news_symbols:
                        if isinstance(sym, str):
                            symbols_found.add(sym.upper())
                    
                    sentiment = getattr(news, 'sentiment', None)
                    if sentiment:
                        sentiment_value = sentiment.value if hasattr(sentiment, 'value') else str(sentiment)
                        if sentiment_value == 'positive':
                            sentiments.append(1)
                        elif sentiment_value == 'negative':
                            sentiments.append(-1)
                        else:
                            sentiments.append(0)
                
                stats["symbols_with_news"] = list(symbols_found)
                if sentiments:
                    stats["avg_sentiment"] = sum(sentiments) / len(sentiments)
            
            self.logger.info(
                f"Notícias coletadas: {stats['news_collected']}, "
                f"símbolos: {len(stats['symbols_with_news'])}"
            )
            
        except Exception as e:
            stats["errors"].append(str(e))
            self.logger.error(f"Erro na coleta de notícias: {e}")
        
        return stats


class OpenInterestCollectionJob(BaseJob):
    """
    Job de coleta de Open Interest.
    
    Intervalo: 5 minutos
    Fontes: Binance Futures
    """
    
    def __init__(self, config: Optional[JobConfig] = None):
        super().__init__(config or OI_COLLECTION_JOB)
        self._collector_manager: Optional[CollectorManager] = None
    
    async def setup(self) -> None:
        """Inicializa o collector manager."""
        self._collector_manager = await get_collector_manager()
    
    async def execute(self) -> Dict[str, Any]:
        """
        Coleta dados de Open Interest.
        
        Returns:
            Dict com estatísticas da coleta
        """
        if not self._collector_manager:
            raise RuntimeError("CollectorManager não inicializado")
        
        stats = {
            "assets_processed": 0,
            "oi_collected": 0,
            "total_oi_usd": 0.0,
            "errors": [],
        }
        
        async with async_session_maker() as session:
            asset_repo = AssetRepository(session)
            
            assets = await asset_repo.get_active_assets()
            symbols = [a.symbol for a in assets]
            stats["assets_processed"] = len(symbols)
            
            try:
                oi_list = await self._collector_manager.collect_open_interest(symbols)
                stats["oi_collected"] = len(oi_list)
                
                for oi_data in oi_list:
                    oi_value = getattr(oi_data, 'open_interest_usd', 0) or 0
                    stats["total_oi_usd"] += oi_value
                
                self.logger.info(
                    f"OI coletado para {stats['oi_collected']} ativos, "
                    f"total: ${stats['total_oi_usd']:,.0f}"
                )
                
            except Exception as e:
                stats["errors"].append(str(e))
                self.logger.error(f"Erro na coleta de OI: {e}")
        
        return stats


class KlineCollectionJob(BaseJob):
    """
    Job de coleta de Klines (candles OHLCV).
    
    Coleta candles de 1h da Binance para análise de volume.
    Isso permite comparar volume atual com volumes históricos
    no mesmo timeframe, evitando z-scores incorretos.
    
    Intervalo: 5 minutos
    Fonte: Binance
    """
    
    # Configurações
    TIMEFRAME = "1h"
    LIMIT = 48  # Últimas 48 horas
    
    def __init__(self, config: Optional[JobConfig] = None):
        super().__init__(config or KLINE_COLLECTION_JOB)
        self._collector_manager: Optional[CollectorManager] = None
    
    async def setup(self) -> None:
        """Inicializa o collector manager."""
        self._collector_manager = await get_collector_manager()
    
    async def execute(self) -> Dict[str, Any]:
        """
        Coleta klines (candles) de todos os ativos.
        
        Returns:
            Dict com estatísticas da coleta
        """
        if not self._collector_manager:
            raise RuntimeError("CollectorManager não inicializado")
        
        stats = {
            "assets_processed": 0,
            "klines_collected": 0,
            "klines_saved": 0,
            "errors": [],
        }
        
        async with async_session_maker() as session:
            asset_repo = AssetRepository(session)
            price_repo = PriceRepository(session)
            
            # Busca ativos ativos
            assets = await asset_repo.get_active_assets()
            symbol_to_id = await asset_repo.get_symbol_id_map()
            
            if not assets:
                self.logger.warning("Nenhum ativo ativo encontrado")
                return stats
            
            self.logger.info(
                f"Coletando klines ({self.TIMEFRAME}) para {len(assets)} ativos"
            )
            
            for asset in assets:
                try:
                    symbol = asset.symbol
                    asset_id = symbol_to_id.get(symbol)
                    
                    if not asset_id:
                        continue
                    
                    # Coleta klines da Binance
                    klines = await self._collector_manager.get_klines(
                        symbol=symbol,
                        timeframe=self.TIMEFRAME,
                        limit=self.LIMIT,
                    )
                    
                    stats["assets_processed"] += 1
                    stats["klines_collected"] += len(klines)
                    
                    # Salva cada kline
                    for kline in klines:
                        try:
                            await price_repo.upsert_price(
                                asset_id=asset_id,
                                timestamp=kline.timestamp,
                                timeframe=self.TIMEFRAME,
                                open_price=kline.open,
                                high_price=kline.high,
                                low_price=kline.low,
                                close_price=kline.close,
                                volume=kline.volume,
                                source="binance",
                            )
                            stats["klines_saved"] += 1
                        except Exception as e:
                            # Ignora erros silenciosamente (duplicatas, etc)
                            pass
                    
                except Exception as e:
                    stats["errors"].append(f"{asset.symbol}: {str(e)}")
                    self.logger.error(f"Erro coletando klines para {asset.symbol}: {e}")
            
            await session.commit()
        
        self.logger.info(
            f"Klines coletados: {stats['klines_collected']}, "
            f"salvos: {stats['klines_saved']}"
        )
        
        return stats


class FullDataCollectionJob(BaseJob):
    """
    Job de coleta completa de dados.
    Executa todos os coletores em sequência.
    """
    
    def __init__(self):
        config = JobConfig(
            job_id="full_data_collection",
            name="Coleta Completa",
            description="Executa todos os coletores de dados",
            interval_seconds=600,
            timeout_seconds=300,
            max_retries=1,
            tags=["collector", "full"],
        )
        super().__init__(config)
        self._collector_manager: Optional[CollectorManager] = None
    
    async def setup(self) -> None:
        """Inicializa o collector manager."""
        self._collector_manager = await get_collector_manager()
    
    async def execute(self) -> Dict[str, Any]:
        """
        Executa coleta completa.
        
        Returns:
            Dict com estatísticas da coleta
        """
        if not self._collector_manager:
            raise RuntimeError("CollectorManager não inicializado")
        
        async with async_session_maker() as session:
            asset_repo = AssetRepository(session)
            assets = await asset_repo.get_active_assets()
            symbols = [a.symbol for a in assets]
        
        self.logger.info(f"Executando coleta completa para {len(symbols)} ativos")
        
        result = await self._collector_manager.collect_all(
            symbols=symbols,
            include_news=True,
        )
        
        stats = {
            "symbols": symbols,
            "prices_count": len(result.get("prices", [])),
            "whales_count": len(result.get("whales", [])),
            "flows_count": len(result.get("exchange_flows", [])),
            "oi_count": len(result.get("open_interest", [])),
            "news_count": len(result.get("news", [])),
            "elapsed_seconds": result.get("elapsed_seconds", 0),
            "errors": result.get("errors", []),
        }
        
        self.logger.info(
            f"Coleta completa: preços={stats['prices_count']}, "
            f"whales={stats['whales_count']}, news={stats['news_count']}"
        )
        
        return stats
