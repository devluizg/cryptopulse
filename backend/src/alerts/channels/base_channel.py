"""
Classe base para canais de notificação.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from loguru import logger


@dataclass
class NotificationPayload:
    """Payload de notificação para enviar pelos canais."""
    
    alert_id: int
    alert_type: str
    severity: str
    title: str
    message: str
    symbol: Optional[str] = None
    asset_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "symbol": self.symbol,
            "asset_id": self.asset_id,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BaseChannel(ABC):
    """
    Classe base abstrata para canais de notificação.
    
    Canais disponíveis:
    - Push (WebSocket/Browser)
    - Email
    - Webhook
    """
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self._send_count = 0
        self._error_count = 0
        self._last_send: Optional[datetime] = None
        self._last_error: Optional[str] = None
    
    @abstractmethod
    async def send(self, payload: NotificationPayload) -> bool:
        """
        Envia notificação pelo canal.
        
        Args:
            payload: Dados da notificação
            
        Returns:
            True se enviou com sucesso
        """
        pass
    
    @abstractmethod
    async def send_batch(self, payloads: list[NotificationPayload]) -> int:
        """
        Envia múltiplas notificações.
        
        Args:
            payloads: Lista de notificações
            
        Returns:
            Número de envios bem-sucedidos
        """
        pass
    
    async def _pre_send(self, payload: NotificationPayload) -> bool:
        """Hook executado antes do envio."""
        if not self.enabled:
            logger.debug(f"Channel {self.name} is disabled, skipping")
            return False
        return True
    
    async def _post_send(self, payload: NotificationPayload, success: bool):
        """Hook executado após o envio."""
        if success:
            self._send_count += 1
            self._last_send = datetime.utcnow()
        else:
            self._error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do canal."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "send_count": self._send_count,
            "error_count": self._error_count,
            "last_send": self._last_send.isoformat() if self._last_send else None,
            "last_error": self._last_error,
        }
