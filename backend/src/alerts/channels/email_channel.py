"""
Canal de notificação por Email.

Nota: Implementação básica - requer configuração SMTP.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

from loguru import logger

from .base_channel import BaseChannel, NotificationPayload


class EmailChannel(BaseChannel):
    """
    Canal de notificação por email.
    
    Requer configuração:
    - SMTP_HOST
    - SMTP_PORT
    - SMTP_USER
    - SMTP_PASSWORD
    - EMAIL_FROM
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        email_from: Optional[str] = None,
    ):
        # Só habilita se tiver configuração
        has_config = all([smtp_host, smtp_user, smtp_password, email_from])
        super().__init__(name="email", enabled=has_config)
        
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.email_from = email_from
        self._recipients: List[str] = []
    
    def add_recipient(self, email: str) -> None:
        """Adiciona destinatário."""
        if email not in self._recipients:
            self._recipients.append(email)
    
    def remove_recipient(self, email: str) -> None:
        """Remove destinatário."""
        if email in self._recipients:
            self._recipients.remove(email)
    
    async def send(self, payload: NotificationPayload) -> bool:
        """
        Envia email com a notificação.
        
        Args:
            payload: Dados da notificação
            
        Returns:
            True se enviou com sucesso
        """
        if not await self._pre_send(payload):
            return False
        
        if not self._recipients:
            logger.debug("No email recipients configured")
            return False
        
        try:
            # TODO: Implementar envio real com aiosmtplib
            # Por enquanto, apenas loga
            logger.info(
                f"[EMAIL] Would send to {self._recipients}: "
                f"{payload.title} - {payload.message[:50]}..."
            )
            
            await self._post_send(payload, True)
            return True
            
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Failed to send email: {e}")
            await self._post_send(payload, False)
            return False
    
    async def send_batch(self, payloads: list[NotificationPayload]) -> int:
        """Envia múltiplos emails."""
        success_count = 0
        for payload in payloads:
            if await self.send(payload):
                success_count += 1
            # Rate limiting
            await asyncio.sleep(0.5)
        return success_count


# Instância global
email_channel = EmailChannel()
