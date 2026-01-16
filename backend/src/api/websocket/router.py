"""
CryptoPulse - WebSocket Router
Endpoints WebSocket
"""

import uuid
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from .manager import ws_manager
from src.utils.logger import logger

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Query(default=None),
):
    """
    Endpoint WebSocket principal
    
    Mensagens suportadas (client -> server):
    - {"type": "subscribe", "channel": "scores|prices|alerts"}
    - {"type": "unsubscribe", "channel": "scores|prices|alerts"}
    - {"type": "ping"}
    
    Mensagens enviadas (server -> client):
    - {"type": "connection", "payload": {...}}
    - {"type": "score_update", "payload": {...}}
    - {"type": "price_update", "payload": {...}}
    - {"type": "alert", "payload": {...}}
    - {"type": "pong"}
    """
    # Gerar client_id se não fornecido
    if not client_id:
        client_id = str(uuid.uuid4())[:8]
    
    # Conectar
    connected = await ws_manager.connect(websocket, client_id)
    if not connected:
        return
    
    try:
        while True:
            # Aguardar mensagem do cliente
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type", "")
                
                if msg_type == "subscribe":
                    channel = message.get("channel", "all")
                    success = await ws_manager.subscribe(client_id, channel)
                    await ws_manager.send_personal(client_id, {
                        "type": "subscribed",
                        "payload": {"channel": channel, "success": success},
                    })
                
                elif msg_type == "unsubscribe":
                    channel = message.get("channel", "all")
                    success = await ws_manager.unsubscribe(client_id, channel)
                    await ws_manager.send_personal(client_id, {
                        "type": "unsubscribed",
                        "payload": {"channel": channel, "success": success},
                    })
                
                elif msg_type == "ping":
                    await ws_manager.send_personal(client_id, {
                        "type": "pong",
                        "payload": {"client_id": client_id},
                    })
                
                else:
                    logger.debug(f"[WebSocket] Mensagem desconhecida de {client_id}: {msg_type}")
                    
            except json.JSONDecodeError:
                logger.warning(f"[WebSocket] JSON inválido de {client_id}: {data[:100]}")
                
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"[WebSocket] Erro com {client_id}: {e}")
        await ws_manager.disconnect(client_id)


@router.get("/ws/stats")
async def websocket_stats():
    """Retorna estatísticas das conexões WebSocket"""
    return ws_manager.get_stats()
