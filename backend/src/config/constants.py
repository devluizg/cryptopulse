"""
Constantes do sistema CryptoPulse.
"""

# =============================================================================
# SCORE THRESHOLDS
# =============================================================================
SCORE_THRESHOLD_HIGH = 70.0       # Score >= 70: Zona de explosão
SCORE_THRESHOLD_ATTENTION = 40.0  # Score >= 40: Zona de atenção
SCORE_THRESHOLD_LOW = 40.0        # Score < 40: Zona normal

# =============================================================================
# INDICATOR WEIGHTS (devem somar 1.0)
# =============================================================================
# AJUSTADO: Prioriza indicadores que têm dados reais disponíveis
# Whale e Netflow têm dados via blockchain/exchanges
# Volume tem dados da Binance (mas precisa histórico)
# OI tem dados parciais da Binance Futures
# Narrative depende de API externa (CryptoPanic)
INDICATOR_WEIGHTS = {
    "whale_accumulation": 0.30,   # 30% - Movimentação de whales (TEM DADOS)
    "exchange_netflow": 0.30,     # 30% - Fluxo de exchanges (TEM DADOS)
    "volume_anomaly": 0.20,       # 20% - Anomalia de volume (PRECISA HISTÓRICO)
    "oi_pressure": 0.15,          # 15% - Open Interest (PARCIAL)
    "narrative_momentum": 0.05,   # 5% - Sentiment/Notícias (SEM API CONFIGURADA)
}

# =============================================================================
# INDICATOR LABELS (para exibição no frontend)
# =============================================================================
INDICATOR_LABELS = {
    "whale_accumulation": "🐋 Whales",
    "exchange_netflow": "📊 Netflow",
    "volume_anomaly": "📈 Volume",
    "oi_pressure": "⚡ Open Interest",
    "narrative_momentum": "📰 Notícias",
}

# =============================================================================
# COLLECTOR SETTINGS
# =============================================================================
COLLECTOR_INTERVALS = {
    "price": 60,           # Coleta de preços a cada 60 segundos
    "whale": 300,          # Coleta de whales a cada 5 minutos
    "news": 600,           # Coleta de notícias a cada 10 minutos
    "open_interest": 300,  # Coleta de OI a cada 5 minutos
}

# =============================================================================
# WHALE SETTINGS
# =============================================================================
WHALE_MIN_TRANSACTION_USD = 1_000_000  # $1M mínimo para considerar whale
WHALE_LOOKBACK_HOURS = 24              # Janela de análise de 24h

# =============================================================================
# ALERT SETTINGS
# =============================================================================
ALERT_SCORE_THRESHOLD = 70.0           # Alerta quando score >= 70
ALERT_SCORE_SPIKE_THRESHOLD = 20.0     # Alerta quando score sobe 20+ pontos
ALERT_WHALE_THRESHOLD_USD = 10_000_000 # Alerta para TX >= $10M

# =============================================================================
# DEFAULT ASSETS
# =============================================================================
DEFAULT_ASSETS = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "coingecko_id": "bitcoin",
        "binance_symbol": "BTCUSDT",
        "priority": 100,
    },
    {
        "symbol": "ETH",
        "name": "Ethereum",
        "coingecko_id": "ethereum",
        "binance_symbol": "ETHUSDT",
        "priority": 90,
    },
    {
        "symbol": "SOL",
        "name": "Solana",
        "coingecko_id": "solana",
        "binance_symbol": "SOLUSDT",
        "priority": 80,
    },
    {
        "symbol": "BNB",
        "name": "BNB",
        "coingecko_id": "binancecoin",
        "binance_symbol": "BNBUSDT",
        "priority": 70,
    },
    {
        "symbol": "XRP",
        "name": "XRP",
        "coingecko_id": "ripple",
        "binance_symbol": "XRPUSDT",
        "priority": 65,
    },
    {
        "symbol": "ADA",
        "name": "Cardano",
        "coingecko_id": "cardano",
        "binance_symbol": "ADAUSDT",
        "priority": 60,
    },
    {
        "symbol": "DOGE",
        "name": "Dogecoin",
        "coingecko_id": "dogecoin",
        "binance_symbol": "DOGEUSDT",
        "priority": 55,
    },
    {
        "symbol": "AVAX",
        "name": "Avalanche",
        "coingecko_id": "avalanche-2",
        "binance_symbol": "AVAXUSDT",
        "priority": 50,
    },
    {
        "symbol": "LINK",
        "name": "Chainlink",
        "coingecko_id": "chainlink",
        "binance_symbol": "LINKUSDT",
        "priority": 45,
    },
    {
        "symbol": "MATIC",
        "name": "Polygon",
        "coingecko_id": "matic-network",
        "binance_symbol": "MATICUSDT",
        "priority": 40,
    },
]

# =============================================================================
# API SETTINGS
# =============================================================================
API_RATE_LIMITS = {
    "binance": 1200,       # 1200 requests/min
    "coingecko": 30,       # 30 requests/min (free tier)
    "etherscan": 5,        # 5 requests/segundo
    "cryptopanic": 100,    # 100 requests/dia
}

# =============================================================================
# CACHE SETTINGS
# =============================================================================
CACHE_TTL = {
    "price": 30,           # Cache de preço: 30 segundos
    "score": 60,           # Cache de score: 60 segundos
    "whale": 300,          # Cache de whale: 5 minutos
    "news": 600,           # Cache de notícias: 10 minutos
}

# =============================================================================
# STATUS LABELS
# =============================================================================
STATUS_LABELS = {
    "high": "🔴 Alta",
    "attention": "🟡 Atenção",
    "low": "🟢 Normal",
}

STATUS_COLORS = {
    "high": "#ef4444",      # Red
    "attention": "#f59e0b", # Yellow
    "low": "#22c55e",       # Green
}
