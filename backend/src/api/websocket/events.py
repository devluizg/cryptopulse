"""
CryptoPulse - WebSocket Events
Funções helper para disparar eventos via WebSocket
"""

from typing import Optional
from .manager import ws_manager
from src.utils.logger import logger


async def emit_score_update(
    asset_id: int,
    symbol: str,
    old_score: float,
    new_score: float,
    status: str,
):
    """Emite evento de atualização de score"""
    try:
        await ws_manager.broadcast_score_update(
            asset_id=asset_id,
            symbol=symbol,
            old_score=old_score,
            new_score=new_score,
            status=status,
        )
        logger.debug(f"[WS Event] Score update: {symbol} {old_score:.1f} -> {new_score:.1f}")
    except Exception as e:
        logger.error(f"[WS Event] Erro ao emitir score_update: {e}")


async def emit_price_update(
    asset_id: int,
    symbol: str,
    price: float,
    change_24h: float,
):
    """Emite evento de atualização de preço"""
    try:
        await ws_manager.broadcast_price_update(
            asset_id=asset_id,
            symbol=symbol,
            price=price,
            change_24h=change_24h,
        )
        logger.debug(f"[WS Event] Price update: {symbol} ${price:.2f}")
    except Exception as e:
        logger.error(f"[WS Event] Erro ao emitir price_update: {e}")


async def emit_alert(
    alert_id: int,
    asset_id: int,
    symbol: str,
    title: str,
    message: str,
    severity: str,
    alert_type: str,
    score_at_trigger: Optional[float] = None,
):
    """Emite evento de novo alerta"""
    try:
        await ws_manager.broadcast_alert(
            alert_id=alert_id,
            asset_id=asset_id,
            symbol=symbol,
            title=title,
            message=message,
            severity=severity,
            alert_type=alert_type,
            score_at_trigger=score_at_trigger,
        )
        logger.info(f"[WS Event] Alert: {symbol} - {title} ({severity})")
    except Exception as e:
        logger.error(f"[WS Event] Erro ao emitir alert: {e}")


async def emit_system_message(message: str, level: str = "info"):
    """Emite mensagem do sistema para todos os clientes"""
    try:
        await ws_manager.broadcast({
            "type": "system",
            "payload": {
                "message": message,
                "level": level,
            },
        })
    except Exception as e:
        logger.error(f"[WS Event] Erro ao emitir system message: {e}")
