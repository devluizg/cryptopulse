"""
CryptoPulse - WebSocket Connection Manager
Gerencia conexões WebSocket ativas
"""

import asyncio
import json
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from src.utils.logger import logger


class WebSocketManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        # Conexões ativas: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Subscriptions: {channel: {client_ids}}
        self.subscriptions: Dict[str, Set[str]] = {
            "scores": set(),
            "prices": set(),
            "alerts": set(),
            "all": set(),
        }
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_id: str) -> bool:
        """Aceita nova conexão WebSocket"""
        try:
            await websocket.accept()
            async with self._lock:
                self.active_connections[client_id] = websocket
                self.subscriptions["all"].add(client_id)
            
            logger.info(f"[WebSocket] Cliente conectado: {client_id}")
            
            # Enviar mensagem de boas-vindas
            await self.send_personal(client_id, {
                "type": "connection",
                "payload": {
                    "status": "connected",
                    "client_id": client_id,
                    "message": "Conectado ao CryptoPulse WebSocket",
                    "channels": list(self.subscriptions.keys()),
                },
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            return True
        except Exception as e:
            logger.error(f"[WebSocket] Erro ao conectar {client_id}: {e}")
            return False
    
    async def disconnect(self, client_id: str):
        """Remove conexão WebSocket"""
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            
            # Remover de todas as subscriptions
            for channel in self.subscriptions.values():
                channel.discard(client_id)
        
        logger.info(f"[WebSocket] Cliente desconectado: {client_id}")
    
    async def subscribe(self, client_id: str, channel: str) -> bool:
        """Inscreve cliente em um canal"""
        if channel not in self.subscriptions:
            return False
        
        async with self._lock:
            self.subscriptions[channel].add(client_id)
        
        logger.debug(f"[WebSocket] {client_id} inscrito em {channel}")
        return True
    
    async def unsubscribe(self, client_id: str, channel: str) -> bool:
        """Remove inscrição de um canal"""
        if channel not in self.subscriptions:
            return False
        
        async with self._lock:
            self.subscriptions[channel].discard(client_id)
        
        logger.debug(f"[WebSocket] {client_id} removido de {channel}")
        return True
    
    async def send_personal(self, client_id: str, message: dict):
        """Envia mensagem para um cliente específico"""
        if client_id not in self.active_connections:
            return
        
        try:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"[WebSocket] Erro ao enviar para {client_id}: {e}")
            await self.disconnect(client_id)
    
    async def broadcast(self, message: dict, channel: str = "all"):
        """Envia mensagem para todos os clientes de um canal"""
        if channel not in self.subscriptions:
            channel = "all"
        
        client_ids = list(self.subscriptions[channel])
        
        for client_id in client_ids:
            await self.send_personal(client_id, message)
    
    async def broadcast_score_update(
        self,
        asset_id: int,
        symbol: str,
        old_score: float,
        new_score: float,
        status: str,
    ):
        """Broadcast de atualização de score"""
        message = {
            "type": "score_update",
            "payload": {
                "asset_id": asset_id,
                "symbol": symbol,
                "old_score": old_score,
                "new_score": new_score,
                "status": status,
                "change": new_score - old_score,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast(message, "scores")
        await self.broadcast(message, "all")
    
    async def broadcast_price_update(
        self,
        asset_id: int,
        symbol: str,
        price: float,
        change_24h: float,
    ):
        """Broadcast de atualização de preço"""
        message = {
            "type": "price_update",
            "payload": {
                "asset_id": asset_id,
                "symbol": symbol,
                "price": price,
                "change_24h": change_24h,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast(message, "prices")
        await self.broadcast(message, "all")
    
    async def broadcast_alert(
        self,
        alert_id: int,
        asset_id: int,
        symbol: str,
        title: str,
        message: str,
        severity: str,
        alert_type: str,
        score_at_trigger: Optional[float] = None,
    ):
        """Broadcast de novo alerta"""
        msg = {
            "type": "alert",
            "payload": {
                "id": alert_id,
                "asset_id": asset_id,
                "symbol": symbol,
                "title": title,
                "message": message,
                "severity": severity,
                "alert_type": alert_type,
                "score_at_trigger": score_at_trigger,
                "is_read": False,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast(msg, "alerts")
        await self.broadcast(msg, "all")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas das conexões"""
        return {
            "total_connections": len(self.active_connections),
            "subscriptions": {
                channel: len(clients)
                for channel, clients in self.subscriptions.items()
            },
        }


# Instância global do manager
ws_manager = WebSocketManager()
