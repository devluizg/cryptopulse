"""
Testes para PriceCollector.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.collectors.price_collector import (
    BinanceCollector,
    CoinGeckoCollector,
    PriceCollector,
    PriceDataPoint,
    OHLCVData,
)


class TestBinanceCollector:
    """Testes para BinanceCollector."""
    
    @pytest.fixture
    def collector(self):
        """Cria instância do coletor."""
        return BinanceCollector()
    
    @pytest.fixture
    def mock_binance_response(self):
        """Resposta simulada da Binance."""
        return [
            {
                "symbol": "BTCUSDT",
                "lastPrice": "45000.50",
                "priceChangePercent": "5.25",
                "highPrice": "46000.00",
                "lowPrice": "43500.00",
                "openPrice": "42750.00",
                "quoteVolume": "2500000000.00",
            },
            {
                "symbol": "ETHUSDT",
                "lastPrice": "2500.25",
                "priceChangePercent": "3.15",
                "highPrice": "2600.00",
                "lowPrice": "2400.00",
                "openPrice": "2425.00",
                "quoteVolume": "1500000000.00",
            },
        ]
    
    def test_get_binance_symbol(self, collector):
        """Testa mapeamento de símbolos."""
        assert collector._get_binance_symbol("BTC") == "BTCUSDT"
        assert collector._get_binance_symbol("ETH") == "ETHUSDT"
        assert collector._get_binance_symbol("INVALID") is None
    
    def test_parse_ticker(self, collector, mock_binance_response):
        """Testa parsing de ticker."""
        ticker = mock_binance_response[0]
        
        result = collector._parse_ticker("BTC", ticker)
        
        assert result.symbol == "BTC"
        assert result.price_usd == 45000.50
        assert result.price_change_24h == 5.25
        assert result.volume_24h == 2500000000.00
        assert result.source == "binance"
    
    @pytest.mark.asyncio
    async def test_collect(self, collector, mock_binance_response):
        """Testa coleta de múltiplos símbolos."""
        collector.get = AsyncMock(return_value=mock_binance_response)
        
        results = await collector.collect(["BTC", "ETH"])
        
        assert len(results) == 2
        assert results[0].symbol == "BTC"
        assert results[1].symbol == "ETH"
    
    @pytest.mark.asyncio
    async def test_collect_single(self, collector):
        """Testa coleta de um único símbolo."""
        mock_response = {
            "symbol": "BTCUSDT",
            "lastPrice": "45000.00",
            "priceChangePercent": "2.5",
            "highPrice": "46000.00",
            "lowPrice": "44000.00",
            "openPrice": "44500.00",
            "quoteVolume": "1000000000.00",
        }
        collector.get = AsyncMock(return_value=mock_response)
        
        result = await collector.collect_single("BTC")
        
        assert result is not None
        assert result.symbol == "BTC"
        assert result.price_usd == 45000.00
    
    @pytest.mark.asyncio
    async def test_collect_single_invalid_symbol(self, collector):
        """Testa coleta de símbolo inválido."""
        result = await collector.collect_single("INVALID")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_klines(self, collector):
        """Testa obtenção de klines (OHLCV)."""
        mock_klines = [
            [1704067200000, "42000.00", "43000.00", "41500.00", "42500.00", "1000.00"],
            [1704153600000, "42500.00", "44000.00", "42000.00", "43500.00", "1200.00"],
        ]
        collector.get = AsyncMock(return_value=mock_klines)
        
        results = await collector.get_klines("BTC", timeframe="1d", limit=2)
        
        assert len(results) == 2
        assert results[0].open == 42000.00
        assert results[0].close == 42500.00
        assert results[0].volume == 1000.00
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, collector):
        """Testa health check quando API está ok."""
        collector.get = AsyncMock(return_value={})
        
        result = await collector.health_check()
        
        assert result["status"] == "healthy"
        assert result["collector"] == "binance"
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, collector):
        """Testa health check quando API falha."""
        collector.get = AsyncMock(side_effect=Exception("Connection error"))
        
        result = await collector.health_check()
        
        assert result["status"] == "unhealthy"
        assert "error" in result


class TestCoinGeckoCollector:
    """Testes para CoinGeckoCollector."""
    
    @pytest.fixture
    def collector(self):
        """Cria instância do coletor."""
        return CoinGeckoCollector()
    
    @pytest.fixture
    def mock_coingecko_response(self):
        """Resposta simulada do CoinGecko."""
        return [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.50,
                "market_cap": 880000000000,
                "total_volume": 25000000000,
                "price_change_percentage_24h": 5.25,
                "high_24h": 46000.00,
                "low_24h": 43500.00,
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 2500.25,
                "market_cap": 300000000000,
                "total_volume": 15000000000,
                "price_change_percentage_24h": 3.15,
                "high_24h": 2600.00,
                "low_24h": 2400.00,
            },
        ]
    
    def test_get_coingecko_id(self, collector):
        """Testa mapeamento de IDs do CoinGecko."""
        assert collector._get_coingecko_id("BTC") == "bitcoin"
        assert collector._get_coingecko_id("ETH") == "ethereum"
        assert collector._get_coingecko_id("INVALID") is None
    
    def test_parse_market_data(self, collector, mock_coingecko_response):
        """Testa parsing de dados de mercado."""
        data = mock_coingecko_response[0]
        
        result = collector._parse_market_data("BTC", data)
        
        assert result.symbol == "BTC"
        assert result.price_usd == 45000.50
        assert result.market_cap == 880000000000
        assert result.source == "coingecko"
    
    @pytest.mark.asyncio
    async def test_collect(self, collector, mock_coingecko_response):
        """Testa coleta de múltiplos símbolos."""
        collector.get = AsyncMock(return_value=mock_coingecko_response)
        
        results = await collector.collect(["BTC", "ETH"])
        
        assert len(results) == 2


class TestPriceCollector:
    """Testes para agregador PriceCollector."""
    
    @pytest.fixture
    def collector(self):
        """Cria instância do agregador."""
        return PriceCollector()
    
    @pytest.mark.asyncio
    async def test_collect_uses_binance_first(self, collector):
        """Testa que Binance é usada primeiro."""
        mock_data = [
            PriceDataPoint(symbol="BTC", price_usd=45000, source="binance")
        ]
        collector.binance.collect = AsyncMock(return_value=mock_data)
        
        results = await collector.collect(["BTC"])
        
        assert len(results) == 1
        assert results[0].source == "binance"
    
    @pytest.mark.asyncio
    async def test_collect_fallback_to_coingecko(self, collector):
        """Testa fallback para CoinGecko quando Binance falha."""
        from src.collectors.base_collector import CollectorError
        
        collector.binance.collect = AsyncMock(side_effect=CollectorError("Error"))
        mock_data = [
            PriceDataPoint(symbol="BTC", price_usd=45000, source="coingecko")
        ]
        collector.coingecko.collect = AsyncMock(return_value=mock_data)
        
        results = await collector.collect(["BTC"])
        
        assert len(results) == 1
        assert results[0].source == "coingecko"
    
    def test_get_metrics(self, collector):
        """Testa obtenção de métricas."""
        metrics = collector.get_metrics()
        
        assert "binance" in metrics
        assert "coingecko" in metrics


class TestPriceDataPoint:
    """Testes para PriceDataPoint."""
    
    def test_create_price_data_point(self):
        """Testa criação de ponto de dados."""
        point = PriceDataPoint(
            symbol="BTC",
            price_usd=45000.0,
            volume_24h=1000000000,
            price_change_24h=5.5,
            source="binance",
        )
        
        assert point.symbol == "BTC"
        assert point.price_usd == 45000.0
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        point = PriceDataPoint(
            symbol="ETH",
            price_usd=2500.0,
            volume_24h=500000000,
            source="coingecko",
        )
        
        result = point.to_dict()
        
        assert result["symbol"] == "ETH"
        assert result["price_usd"] == 2500.0
        assert result["source"] == "coingecko"
