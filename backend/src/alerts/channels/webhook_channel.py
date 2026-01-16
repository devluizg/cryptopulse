"""
Canal de notificação via Webhook.

Envia alertas para URLs externas (Discord, Slack, Telegram bots, etc).
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import asyncio

import httpx
from loguru import logger

from .base_channel import BaseChannel, NotificationPayload


@dataclass
class WebhookConfig:
    """Configuração de um webhook."""
    
    name: str
    url: str
    enabled: bool = True
    
    # Filtros
    min_severity: str = "low"  # Só envia se severidade >= min_severity
    alert_types: Optional[List[str]] = None  # None = todos
    symbols: Optional[List[str]] = None  # None = todos
    
    # Headers customizados
    headers: Optional[Dict[str, str]] = field(default_factory=dict)


class WebhookChannel(BaseChannel):
    """
    Canal de notificação via webhooks HTTP.
    
    Suporta múltiplos webhooks com filtros diferentes.
    """
    
    SEVERITY_ORDER = ["info", "low", "medium", "high", "critical"]
    
    def __init__(self):
        super().__init__(name="webhook", enabled=True)
        self._webhooks: Dict[str, WebhookConfig] = {}
        self._client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """Inicializa cliente HTTP."""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=10.0)
    
    async def shutdown(self):
        """Fecha cliente HTTP."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def add_webhook(self, config: WebhookConfig) -> None:
        """Adiciona um webhook."""
        self._webhooks[config.name] = config
        logger.info(f"Webhook added: {config.name}")
    
    def remove_webhook(self, name: str) -> None:
        """Remove um webhook."""
        if name in self._webhooks:
            del self._webhooks[name]
    
    def _should_send(
        self,
        webhook: WebhookConfig,
        payload: NotificationPayload,
    ) -> bool:
        """Verifica se deve enviar para este webhook."""
        if not webhook.enabled:
            return False
        
        # Verifica severidade mínima
        try:
            payload_severity_idx = self.SEVERITY_ORDER.index(payload.severity)
            min_severity_idx = self.SEVERITY_ORDER.index(webhook.min_severity)
            if payload_severity_idx < min_severity_idx:
                return False
        except ValueError:
            pass
        
        # Verifica tipo de alerta
        if webhook.alert_types and payload.alert_type not in webhook.alert_types:
            return False
        
        # Verifica símbolo
        if webhook.symbols and payload.symbol not in webhook.symbols:
            return False
        
        return True
    
    async def send(self, payload: NotificationPayload) -> bool:
        """
        Envia notificação para todos os webhooks aplicáveis.
        
        Args:
            payload: Dados da notificação
            
        Returns:
            True se enviou para pelo menos um webhook
        """
        if not await self._pre_send(payload):
            return False
        
        if not self._webhooks:
            return False
        
        await self.initialize()
        
        if self._client is None:
            logger.error("HTTP client not initialized")
            return False
        
        success_count = 0
        
        for name, webhook in self._webhooks.items():
            if not self._should_send(webhook, payload):
                continue
            
            try:
                headers = {"Content-Type": "application/json"}
                if webhook.headers:
                    headers.update(webhook.headers)
                
                response = await self._client.post(
                    webhook.url,
                    json=payload.to_dict(),
                    headers=headers,
                )
                
                if response.status_code < 300:
                    success_count += 1
                    logger.debug(f"Webhook {name} sent successfully")
                else:
                    logger.warning(
                        f"Webhook {name} returned {response.status_code}"
                    )
                    
            except Exception as e:
                logger.error(f"Webhook {name} failed: {e}")
        
        success = success_count > 0
        await self._post_send(payload, success)
        
        return success
    
    async def send_batch(self, payloads: list[NotificationPayload]) -> int:
        """Envia múltiplas notificações."""
        success_count = 0
        for payload in payloads:
            if await self.send(payload):
                success_count += 1
            await asyncio.sleep(0.1)  # Rate limiting
        return success_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas incluindo webhooks."""
        stats = super().get_stats()
        stats["webhooks"] = {
            name: {"enabled": wh.enabled, "url": wh.url[:30] + "..."}
            for name, wh in self._webhooks.items()
        }
        return stats


# Instância global
webhook_channel = WebhookChannel()
