"""
Gerenciador do Engine de Cálculo.

Coordena:
- Coleta de dados dos collectors
- Preparação de dados para indicadores
- Cálculo de scores
- Persistência no banco
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from .score_calculator import ScoreCalculator
from ..database.repositories import (
    AssetRepository,
    ScoreRepository,
    WhaleRepository,
    PriceRepository,
)
from ..database.connection import async_session_maker
from ..config.constants import INDICATOR_LABELS


# Labels legíveis para os indicadores
DRIVER_LABELS = {
    "whale_accumulation": "🐋 Whales",
    "exchange_netflow": "📊 Netflow",
    "volume_anomaly": "📈 Volume",
    "oi_pressure": "⚡ OI",
    "narrative_momentum": "📰 News",
}


def generate_main_drivers(indicator_scores: Dict[str, float], indicator_details: Dict[str, Any]) -> str:
    """
    Gera texto legível dos principais drivers do score.
    
    Em vez de: "exchange_netflow: 69, whale_accumulation: 62"
    Mostra: "🐋 Whales acumulando | 📊 Saída de exchanges"
    """
    drivers = []
    
    # Ordenar por score (maior primeiro)
    sorted_indicators = sorted(
        indicator_scores.items(),
        key=lambda x: abs(x[1] - 50),  # Distância do neutro (50)
        reverse=True
    )
    
    for indicator_key, score in sorted_indicators[:2]:  # Top 2
        label = DRIVER_LABELS.get(indicator_key, indicator_key)
        details = indicator_details.get(indicator_key, {})
        reason = details.get("reason", "")
        
        # Simplificar o texto
        if indicator_key == "whale_accumulation":
            direction = details.get("net_direction", "")
            if direction == "accumulation":
                drivers.append(f"{label} acumulando")
            elif direction == "distribution":
                drivers.append(f"{label} distribuindo")
            else:
                drivers.append(f"{label} ({score:.0f})")
                
        elif indicator_key == "exchange_netflow":
            interpretation = details.get("interpretation", "")
            if "accumulation" in interpretation:
                drivers.append(f"{label} saída (bullish)")
            elif "distribution" in interpretation:
                drivers.append(f"{label} entrada (bearish)")
            else:
                drivers.append(f"{label} ({score:.0f})")
                
        elif indicator_key == "volume_anomaly":
            z_score = details.get("z_score")
            if z_score and z_score > 2:
                drivers.append(f"{label} muito alto")
            elif z_score and z_score > 1:
                drivers.append(f"{label} elevado")
            elif z_score and z_score < -1:
                drivers.append(f"{label} baixo")
            else:
                drivers.append(f"{label} normal")
                
        elif indicator_key == "oi_pressure":
            interpretation = details.get("interpretation", "")
            if interpretation == "bullish":
                drivers.append(f"{label} alta (bullish)")
            elif interpretation == "bearish":
                drivers.append(f"{label} queda (bearish)")
            else:
                drivers.append(f"{label} neutro")
                
        elif indicator_key == "narrative_momentum":
            news_count = details.get("news_count", 0)
            if news_count > 5:
                drivers.append(f"{label} alta atividade")
            elif news_count > 0:
                drivers.append(f"{label} ({news_count} notícias)")
            else:
                drivers.append(f"{label} sem dados")
        else:
            drivers.append(f"{label} ({score:.0f})")
    
    return " | ".join(drivers) if drivers else "Dados insuficientes"


class EngineManager:
    """
    Gerenciador central do motor de cálculo.
    
    Responsabilidades:
    - Orquestrar coleta de dados
    - Preparar dados para cada indicador
    - Executar cálculos
    - Salvar resultados
    - Gerenciar ciclo de atualização
    """
    
    def __init__(self):
        """Inicializa o Engine Manager."""
        self.calculator = ScoreCalculator()
        self.collector_manager = None
        self._initialized = False
        self._last_run: Optional[datetime] = None
        self._run_count = 0
    
    async def initialize(self, collector_manager=None):
        """
        Inicializa o engine.
        
        Args:
            collector_manager: Instância do CollectorManager (opcional)
        """
        if collector_manager:
            self.collector_manager = collector_manager
        else:
            from ..collectors.collector_manager import CollectorManager
            self.collector_manager = CollectorManager()
            await self.collector_manager.initialize()
        
        self._initialized = True
        logger.info("[EngineManager] Inicializado")
    
    async def shutdown(self):
        """Finaliza o engine."""
        if self.collector_manager:
            try:
                await self.collector_manager.close()
            except Exception as e:
                logger.error(f"[EngineManager] Erro ao finalizar collector_manager: {e}")
        
        self._initialized = False
        logger.info("[EngineManager] Finalizado")
    
    async def run_calculation_cycle(self) -> Dict[str, Any]:
        """
        Executa um ciclo completo de cálculo.
        
        1. Coleta dados atualizados
        2. Calcula scores para todos os ativos
        3. Persiste resultados
        4. Retorna resumo
        
        Returns:
            Dict com resultados do ciclo
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = datetime.utcnow()
        logger.info("[EngineManager] Iniciando ciclo de cálculo")
        
        results = {
            "start_time": start_time,
            "assets_processed": 0,
            "scores_created": 0,
            "errors": [],
            "scores": {},
        }
        
        async with async_session_maker() as session:
            # Repositórios
            asset_repo = AssetRepository(session)
            score_repo = ScoreRepository(session)
            whale_repo = WhaleRepository(session)
            price_repo = PriceRepository(session)
            
            # Buscar ativos ativos
            assets = await asset_repo.get_active_assets()
            
            if not assets:
                logger.warning("[EngineManager] Nenhum ativo ativo encontrado")
                return results
            
            logger.info(f"[EngineManager] Processando {len(assets)} ativos")
            
            # Coletar dados gerais (uma vez)
            collected_data = {}
            prices_map = {}  # Mapa symbol -> PriceDataPoint
            
            if self.collector_manager:
                try:
                    symbols = [a.symbol for a in assets]
                    collected_data = await self.collector_manager.collect_all(symbols)
                    
                    # Criar mapa de preços por símbolo
                    prices_list = collected_data.get("prices", [])
                    for price_data in prices_list:
                        if hasattr(price_data, 'symbol'):
                            prices_map[price_data.symbol] = price_data
                    
                    logger.info(f"[EngineManager] Preços coletados: {list(prices_map.keys())}")
                    
                except Exception as e:
                    logger.error(f"[EngineManager] Erro na coleta: {e}")
                    results["errors"].append(f"Coleta: {str(e)}")
            
            # Processar cada ativo
            for asset in assets:
                try:
                    # Preparar dados para o ativo
                    data = await self._prepare_asset_data(
                        asset=asset,
                        collected_data=collected_data,
                        whale_repo=whale_repo,
                        price_repo=price_repo,
                    )
                    
                    # Calcular score
                    score_result = await self.calculator.calculate(data)
                    
                    # Gerar main_drivers legível
                    indicator_scores = score_result.get("indicator_scores", {})
                    indicator_details = score_result.get("indicator_details", {})
                    main_drivers = generate_main_drivers(indicator_scores, indicator_details)
                    
                    # =============================================
                    # USAR DADOS DO COLLECTOR (não do banco!)
                    # A Binance já retorna preço, variação e volume corretos
                    # =============================================
                    price_data = prices_map.get(asset.symbol)
                    
                    if price_data:
                        # Dados frescos da API da Binance
                        price_usd = price_data.price_usd
                        price_change_24h = price_data.price_change_24h
                        volume_24h = price_data.volume_24h
                        
                        logger.debug(
                            f"[EngineManager] {asset.symbol} - Dados da API: "
                            f"price=${price_usd:.2f}, change={price_change_24h:.2f}%, "
                            f"volume=${volume_24h:,.0f}"
                        )
                    else:
                        # Fallback: buscar do banco (menos preciso)
                        logger.warning(f"[EngineManager] {asset.symbol} - Sem dados da API, usando banco")
                        latest_price = await price_repo.get_latest(asset.id)
                        price_usd = latest_price.close if latest_price else None
                        price_change_24h = await price_repo.get_price_change(asset.id, hours=24)
                        volume_24h = latest_price.volume if latest_price else None
                    
                    # =============================================
                    # Salvar no banco COM dados de preço corretos
                    # =============================================
                    score = await score_repo.create_score(
                        asset_id=asset.id,
                        explosion_score=score_result["explosion_score"],
                        status=score_result["status"],
                        whale_accumulation_score=indicator_scores.get("whale_accumulation", 50),
                        exchange_netflow_score=indicator_scores.get("exchange_netflow", 50),
                        volume_anomaly_score=indicator_scores.get("volume_anomaly", 50),
                        oi_pressure_score=indicator_scores.get("oi_pressure", 50),
                        narrative_momentum_score=indicator_scores.get("narrative_momentum", 50),
                        price_usd=price_usd,
                        price_change_24h=price_change_24h,
                        volume_24h=volume_24h,
                        calculation_details=score_result.get("indicator_details", {}),
                        main_drivers=main_drivers,
                    )
                    
                    results["scores"][asset.symbol] = {
                        "score": score_result["explosion_score"],
                        "status": score_result["status"],
                        "price_usd": price_usd,
                        "price_change_24h": price_change_24h,
                        "volume_24h": volume_24h,
                        "main_drivers": main_drivers,
                        "id": score.id,
                    }
                    results["scores_created"] += 1
                    
                    logger.debug(
                        f"[EngineManager] {asset.symbol}: "
                        f"score={score_result['explosion_score']:.1f}, "
                        f"price=${price_usd or 0:.2f}, "
                        f"change={price_change_24h or 0:.2f}%"
                    )
                    
                except Exception as e:
                    logger.error(f"[EngineManager] Erro ao processar {asset.symbol}: {e}")
                    results["errors"].append(f"{asset.symbol}: {str(e)}")
                
                results["assets_processed"] += 1
            
            # Commit
            await session.commit()
        
        # Finalizar
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        results["end_time"] = end_time
        results["duration_seconds"] = duration
        
        self._last_run = end_time
        self._run_count += 1
        
        logger.info(
            f"[EngineManager] Ciclo completo: "
            f"{results['scores_created']} scores em {duration:.2f}s"
        )
        
        return results
    
    async def calculate_single_asset(self, symbol: str) -> Dict[str, Any]:
        """
        Calcula score para um único ativo.
        
        Args:
            symbol: Símbolo do ativo (ex: 'BTC')
            
        Returns:
            Resultado do cálculo
        """
        if not self._initialized:
            await self.initialize()
        
        async with async_session_maker() as session:
            asset_repo = AssetRepository(session)
            score_repo = ScoreRepository(session)
            whale_repo = WhaleRepository(session)
            price_repo = PriceRepository(session)
            
            # Buscar ativo
            asset = await asset_repo.get_by_symbol(symbol.upper())
            if not asset:
                raise ValueError(f"Ativo não encontrado: {symbol}")
            
            # Coletar dados
            collected_data = {}
            price_data = None
            
            if self.collector_manager:
                collected_data = await self.collector_manager.collect_for_symbol(symbol)
                price_data = collected_data.get("price")
            
            # Preparar dados
            data = await self._prepare_asset_data(
                asset=asset,
                collected_data=collected_data,
                whale_repo=whale_repo,
                price_repo=price_repo,
            )
            
            # Calcular
            result = await self.calculator.calculate(data)
            
            # Gerar main_drivers legível
            indicator_scores = result.get("indicator_scores", {})
            indicator_details = result.get("indicator_details", {})
            main_drivers = generate_main_drivers(indicator_scores, indicator_details)
            
            # =============================================
            # USAR DADOS DO COLLECTOR
            # =============================================
            if price_data:
                price_usd = price_data.price_usd
                price_change_24h = price_data.price_change_24h
                volume_24h = price_data.volume_24h
            else:
                latest_price = await price_repo.get_latest(asset.id)
                price_usd = latest_price.close if latest_price else None
                price_change_24h = await price_repo.get_price_change(asset.id, hours=24)
                volume_24h = latest_price.volume if latest_price else None
            
            # Salvar
            score = await score_repo.create_score(
                asset_id=asset.id,
                explosion_score=result["explosion_score"],
                status=result["status"],
                whale_accumulation_score=indicator_scores.get("whale_accumulation", 50),
                exchange_netflow_score=indicator_scores.get("exchange_netflow", 50),
                volume_anomaly_score=indicator_scores.get("volume_anomaly", 50),
                oi_pressure_score=indicator_scores.get("oi_pressure", 50),
                narrative_momentum_score=indicator_scores.get("narrative_momentum", 50),
                price_usd=price_usd,
                price_change_24h=price_change_24h,
                volume_24h=volume_24h,
                calculation_details=result.get("indicator_details", {}),
                main_drivers=main_drivers,
            )
            
            await session.commit()
            
            result["score_id"] = score.id
            result["price_usd"] = price_usd
            result["price_change_24h"] = price_change_24h
            result["volume_24h"] = volume_24h
            result["main_drivers"] = main_drivers
            return result
    
    async def _prepare_asset_data(
        self,
        asset,
        collected_data: Dict[str, Any],
        whale_repo: WhaleRepository,
        price_repo: PriceRepository,
    ) -> Dict[str, Any]:
        """
        Prepara dados para cálculo de um ativo específico.
        """
        symbol = asset.symbol
        
        # Dados de whale do banco
        whale_txs = await whale_repo.get_by_symbol(symbol, hours=24)
        whale_stats = await whale_repo.get_stats_by_asset(asset.id, hours=24)
        
        whale_data = {
            "transactions": [
                {
                    "amount_usd": tx.amount_usd,
                    "transaction_type": tx.transaction_type,
                    "timestamp": tx.timestamp,
                    "to_exchange": tx.is_exchange_inflow,
                    "from_exchange": tx.is_exchange_outflow,
                }
                for tx in whale_txs
            ],
            "historical_avg_volume": whale_stats.get("avg_volume_24h", 0),
            "historical_avg_count": whale_stats.get("avg_count_24h", 0),
        }
        
        # Dados de netflow (estimado via whale transactions)
        netflow = await whale_repo.get_netflow(asset.id, hours=24)
        netflow_data = {
            "inflow_usd": netflow.get("inflow", 0),
            "outflow_usd": netflow.get("outflow", 0),
            "historical_netflows": [],
        }
        
        # =============================================
        # CORREÇÃO: Buscar volumes de 1h do banco (klines reais)
        # Agora compara volume 1h com volume 1h (mesmo timeframe)
        # =============================================
        price_history_1h = await price_repo.get_history(
            asset.id, 
            hours=48,  # Últimas 48 horas
            timeframe="1h"  # Timeframe de 1 hora
        )
        
        # Extrair volumes de 1h (filtra zeros e nulos)
        volumes_1h = [p.volume for p in price_history_1h if p.volume and p.volume > 0]
        
        # Calcular price change
        price_change = 0.0
        latest_price = await price_repo.get_latest(asset.id)
        if latest_price:
            price_change = latest_price.change_pct
        
        # Volume atual = último candle de 1h
        current_volume_1h = 0
        if volumes_1h:
            current_volume_1h = volumes_1h[-1]
        
        # Tentar pegar price_change dos dados coletados (mais preciso)
        prices_list = collected_data.get("prices", [])
        for price_data in prices_list:
            if hasattr(price_data, 'symbol') and price_data.symbol == symbol:
                if hasattr(price_data, 'price_change_24h') and price_data.price_change_24h:
                    price_change = price_data.price_change_24h
                break
        
        # Volume data com timeframes consistentes
        # historical_volumes exclui o atual para não enviesar o cálculo
        volume_data = {
            "current_volume": current_volume_1h,
            "historical_volumes": volumes_1h[:-1] if len(volumes_1h) > 1 else [],
            "price_change_percent": price_change,
        }
        
        # Log para debug
        if volumes_1h:
            logger.debug(
                f"[EngineManager] {symbol} volume data (1h): "
                f"current={current_volume_1h:,.0f}, "
                f"historical_count={len(volumes_1h)-1}"
            )
        else:
            logger.warning(f"[EngineManager] {symbol}: Sem dados de volume 1h no banco. Execute o KlineCollectionJob.")
        
        # Dados de OI (do collector se disponível)
        # Dados de OI (do collector se disponível)
        oi_data = {}
        if collected_data:
            oi_raw = collected_data.get("open_interest", [])
            # Pode ser lista (collect_all) ou objeto único (collect_for_symbol)
            if oi_raw:
                oi_items = oi_raw if isinstance(oi_raw, list) else [oi_raw]
                for oi_item in oi_items:
                    if hasattr(oi_item, "symbol") and oi_item.symbol == symbol:
                        oi_data = {
                            "current_oi": getattr(oi_item, "open_interest", 0),
                            "previous_oi": getattr(oi_item, "previous_oi", 0),
                            "funding_rate": getattr(oi_item, "funding_rate", 0),
                            "long_short_ratio": getattr(oi_item, "long_short_ratio", 1),
                            "price_change_percent": price_change,
                        }
                        break
        
        # Dados de narrativa (do collector se disponível)
        narrative_data = {}
        if collected_data:
            news_list = collected_data.get("news", [])
            if news_list:
                asset_news = []
                for news_item in news_list:
                    title = getattr(news_item, 'title', '') or ''
                    symbols_list = getattr(news_item, 'symbols', []) or []
                    if symbol.lower() in title.lower() or symbol.upper() in [s.upper() for s in symbols_list]:
                        asset_news.append({
                            "title": title,
                            "sentiment": getattr(news_item, 'sentiment', 'neutral'),
                            "published_at": getattr(news_item, 'published_at', None),
                        })
                
                narrative_data = {
                    "news": asset_news[:20],
                    "mention_count": len(asset_news),
                    "historical_mention_avg": 10,
                }
        
        return {
            "asset_symbol": symbol,
            "whale_data": whale_data,
            "netflow_data": netflow_data,
            "volume_data": volume_data,
            "oi_data": oi_data,
            "narrative_data": narrative_data,
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do engine."""
        collector_status = None
        if self.collector_manager:
            try:
                collector_status = self.collector_manager.get_metrics()
            except Exception:
                collector_status = {"error": "Não disponível"}
        
        return {
            "initialized": self._initialized,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "run_count": self._run_count,
            "calculator_status": self.calculator.get_indicator_status(),
            "collector_status": collector_status,
        }
