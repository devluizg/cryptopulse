"""
Canal de notificação Push (WebSocket/In-App).

Envia alertas em tempo real para o frontend via WebSocket.
"""

from typing import Dict, Any, Optional, Set
from datetime import datetime
import asyncio
import json

from loguru import logger

from .base_channel import BaseChannel, NotificationPayload


class PushChannel(BaseChannel):
    """
    Canal de notificação push via WebSocket.
    
    Mantém lista de conexões ativas e envia alertas em tempo real.
    """
    
    def __init__(self):
        super().__init__(name="push", enabled=True)
        self._connections: Set = set()
        self._pending_notifications: list[NotificationPayload] = []
    
    def register_connection(self, websocket) -> None:
        """Registra uma nova conexão WebSocket."""
        self._connections.add(websocket)
        logger.info(f"WebSocket registered. Total connections: {len(self._connections)}")
    
    def unregister_connection(self, websocket) -> None:
        """Remove uma conexão WebSocket."""
        self._connections.discard(websocket)
        logger.info(f"WebSocket unregistered. Total connections: {len(self._connections)}")
    
    @property
    def connection_count(self) -> int:
        """Número de conexões ativas."""
        return len(self._connections)
    
    async def send(self, payload: NotificationPayload) -> bool:
        """
        Envia notificação para todas as conexões WebSocket.
        
        Args:
            payload: Dados da notificação
            
        Returns:
            True se enviou para pelo menos uma conexão
        """
        if not await self._pre_send(payload):
            return False
        
        if not self._connections:
            # Guarda para enviar quando houver conexão
            self._pending_notifications.append(payload)
            logger.debug("No WebSocket connections, notification queued")
            return True
        
        message = json.dumps({
            "type": "alert",
            "payload": payload.to_dict(),
        })
        
        success_count = 0
        dead_connections = set()
        
        for ws in self._connections:
            try:
                await ws.send_text(message)
                success_count += 1
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                dead_connections.add(ws)
        
        # Remove conexões mortas
        for ws in dead_connections:
            self._connections.discard(ws)
        
        success = success_count > 0
        await self._post_send(payload, success)
        
        if success:
            logger.debug(f"Push sent to {success_count} connections")
        
        return success
    
    async def send_batch(self, payloads: list[NotificationPayload]) -> int:
        """Envia múltiplas notificações."""
        success_count = 0
        for payload in payloads:
            if await self.send(payload):
                success_count += 1
        return success_count
    
    async def send_pending(self) -> int:
        """Envia notificações pendentes."""
        if not self._pending_notifications or not self._connections:
            return 0
        
        pending = self._pending_notifications.copy()
        self._pending_notifications.clear()
        
        return await self.send_batch(pending)
    
    async def broadcast(self, message: Dict[str, Any]) -> int:
        """
        Envia mensagem genérica para todas as conexões.
        
        Args:
            message: Dicionário com mensagem
            
        Returns:
            Número de envios bem-sucedidos
        """
        if not self._connections:
            return 0
        
        text = json.dumps(message)
        success_count = 0
        dead_connections = set()
        
        for ws in self._connections:
            try:
                await ws.send_text(text)
                success_count += 1
            except Exception:
                dead_connections.add(ws)
        
        for ws in dead_connections:
            self._connections.discard(ws)
        
        return success_count


# Instância global (singleton)
push_channel = PushChannel()
