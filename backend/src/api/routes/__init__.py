"""
API Routes Package.
"""

from src.api.routes import health
from src.api.routes import assets
from src.api.routes import signals
from src.api.routes import alerts
from src.api.routes import jobs

__all__ = [
    "health",
    "assets",
    "signals",
    "alerts",
    "jobs",
]
