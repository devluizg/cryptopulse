"""
CryptoPulse - Database Configuration
Configurações específicas do banco de dados.
"""

from .settings import settings

# Configurações de pool de conexões
POOL_SIZE = settings.database_pool_size
MAX_OVERFLOW = settings.database_max_overflow
POOL_TIMEOUT = 30
POOL_RECYCLE = 1800

# URL do banco
DATABASE_URL = settings.database_url

# Echo SQL (mostra queries no log - útil para debug)
DATABASE_ECHO = settings.debug
