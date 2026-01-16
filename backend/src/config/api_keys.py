"""
Configuração centralizada de API Keys.
"""

from typing import Optional, List


class APIKeys:
    """Classe para acesso centralizado às API keys."""
    
    @property
    def binance_api_key(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.binance_api_key
    
    @property
    def binance_api_secret(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.binance_api_secret
    
    @property
    def coingecko_api_key(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.coingecko_api_key
    
    @property
    def whale_alert_api_key(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.whale_alert_api_key
    
    @property
    def etherscan_api_key(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.etherscan_api_key
    
    @property
    def cryptopanic_api_key(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.cryptopanic_api_key
    
    @property
    def cryptoquant_api_key(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.cryptoquant_api_key
    
    @property
    def glassnode_api_key(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.glassnode_api_key
    
    @property
    def twitter_bearer_token(self) -> Optional[str]:
        from src.config.settings import settings
        return settings.twitter_bearer_token
    
    def has_key(self, service: str) -> bool:
        key_map = {
            "binance": self.binance_api_key,
            "coingecko": self.coingecko_api_key,
            "whale_alert": self.whale_alert_api_key,
            "etherscan": self.etherscan_api_key,
            "cryptopanic": self.cryptopanic_api_key,
            "cryptoquant": self.cryptoquant_api_key,
            "glassnode": self.glassnode_api_key,
            "twitter": self.twitter_bearer_token,
        }
        key = key_map.get(service.lower())
        return key is not None and len(key) > 0
    
    def get_available_keys(self) -> List[str]:
        services = ["binance", "coingecko", "whale_alert", "etherscan",
                    "cryptopanic", "cryptoquant", "glassnode", "twitter"]
        return [s for s in services if self.has_key(s)]


api_keys = APIKeys()
