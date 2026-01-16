"""
CryptoPulse - Dados de exemplo para testes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any


def get_sample_assets() -> List[Dict[str, Any]]:
    """Retorna lista de assets de exemplo."""
    return [
        {
            "symbol": "BTC",
            "name": "Bitcoin",
            "coingecko_id": "bitcoin",
            "binance_symbol": "BTCUSDT",
            "priority": 100,
            "is_active": True,
        },
        {
            "symbol": "ETH",
            "name": "Ethereum",
            "coingecko_id": "ethereum",
            "binance_symbol": "ETHUSDT",
            "priority": 90,
            "is_active": True,
        },
        {
            "symbol": "SOL",
            "name": "Solana",
            "coingecko_id": "solana",
            "binance_symbol": "SOLUSDT",
            "priority": 80,
            "is_active": True,
        },
    ]


def get_sample_scores() -> List[Dict[str, Any]]:
    """Retorna lista de scores de exemplo."""
    now = datetime.utcnow()
    return [
        {
            "explosion_score": 85.0,
            "status": "high",
            "whale_accumulation_score": 90.0,
            "exchange_netflow_score": 85.0,
            "volume_anomaly_score": 80.0,
            "oi_pressure_score": 75.0,
            "narrative_momentum_score": 95.0,
            "price_usd": 45000.0,
            "price_change_24h": 8.5,
            "calculated_at": now,
        },
        {
            "explosion_score": 55.0,
            "status": "attention",
            "whale_accumulation_score": 60.0,
            "exchange_netflow_score": 55.0,
            "volume_anomaly_score": 50.0,
            "oi_pressure_score": 45.0,
            "narrative_momentum_score": 65.0,
            "price_usd": 2500.0,
            "price_change_24h": 3.2,
            "calculated_at": now,
        },
        {
            "explosion_score": 30.0,
            "status": "low",
            "whale_accumulation_score": 35.0,
            "exchange_netflow_score": 25.0,
            "volume_anomaly_score": 30.0,
            "oi_pressure_score": 40.0,
            "narrative_momentum_score": 20.0,
            "price_usd": 100.0,
            "price_change_24h": -2.1,
            "calculated_at": now,
        },
    ]


def get_sample_whale_transactions() -> List[Dict[str, Any]]:
    """Retorna transações de whale de exemplo."""
    now = datetime.utcnow()
    return [
        {
            "hash": "0x1234567890abcdef",
            "amount_usd": 10_000_000,
            "amount_crypto": 220.5,
            "transaction_type": "outflow",
            "from_exchange": True,
            "to_exchange": False,
            "timestamp": now.isoformat(),
        },
        {
            "hash": "0xabcdef1234567890",
            "amount_usd": 5_000_000,
            "amount_crypto": 110.2,
            "transaction_type": "inflow",
            "from_exchange": False,
            "to_exchange": True,
            "timestamp": (now - timedelta(hours=1)).isoformat(),
        },
        {
            "hash": "0x9876543210fedcba",
            "amount_usd": 3_000_000,
            "amount_crypto": 66.7,
            "transaction_type": "outflow",
            "from_exchange": True,
            "to_exchange": False,
            "timestamp": (now - timedelta(hours=3)).isoformat(),
        },
    ]


def get_sample_alerts() -> List[Dict[str, Any]]:
    """Retorna alertas de exemplo."""
    now = datetime.utcnow()
    return [
        {
            "alert_type": "score_critical",
            "severity": "critical",
            "title": "🚨 BTC em NÍVEL CRÍTICO",
            "message": "Bitcoin atingiu score 92.0! Condições extremas detectadas.",
            "trigger_value": 92.0,
            "score_at_trigger": 92.0,
            "price_at_trigger": 48000.0,
            "is_read": False,
            "created_at": now,
        },
        {
            "alert_type": "whale_large_tx",
            "severity": "high",
            "title": "🐋 BTC - Movimentação de $15M",
            "message": "Whale moveu 330.5 BTC ($15,000,000). Tipo: outflow.",
            "trigger_value": 15_000_000,
            "is_read": False,
            "created_at": now - timedelta(hours=2),
        },
        {
            "alert_type": "score_high",
            "severity": "medium",
            "title": "🔴 ETH entrou em zona de explosão",
            "message": "Ethereum atingiu score 75.0 (zona alta).",
            "trigger_value": 75.0,
            "score_at_trigger": 75.0,
            "is_read": True,
            "created_at": now - timedelta(days=1),
        },
    ]


def get_binance_ticker_response() -> List[Dict[str, Any]]:
    """Retorna resposta simulada da API da Binance."""
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
        {
            "symbol": "SOLUSDT",
            "lastPrice": "100.50",
            "priceChangePercent": "-2.35",
            "highPrice": "105.00",
            "lowPrice": "98.00",
            "openPrice": "103.00",
            "quoteVolume": "500000000.00",
        },
    ]


def get_coingecko_markets_response() -> List[Dict[str, Any]]:
    """Retorna resposta simulada da API do CoinGecko."""
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
