"""
Configurações centralizadas da aplicação.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


def find_env_file() -> Optional[str]:
    """Procura o arquivo .env em locais comuns."""
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / ".env",
        Path(__file__).parent.parent.parent / ".env",
        Path.cwd() / ".env",
    ]
    for path in possible_paths:
        if path.exists():
            return str(path)
    return None


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Aplicação
    app_name: str = "CryptoPulse"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    database_url: str = "postgresql+asyncpg://cryptopulse:cryptopulse123@localhost:5434/cryptopulse"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Redis
    redis_url: str = "redis://localhost:6380/0"
    
    # API Keys
    binance_api_key: Optional[str] = None
    binance_api_secret: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    whale_alert_api_key: Optional[str] = None
    etherscan_api_key: Optional[str] = None
    cryptoquant_api_key: Optional[str] = None
    glassnode_api_key: Optional[str] = None
    cryptopanic_api_key: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    coinmarketcap_api_key: Optional[str] = None
    newsapi_api_key: Optional[str] = None
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ("development", "dev", "local")
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")


settings = Settings()
