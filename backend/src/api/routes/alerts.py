"""
CryptoPulse - Alert Routes
Endpoints para gerenciamento de alertas
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.connection import get_session
from src.database.repositories import AssetRepository, AlertRepository
from src.api.schemas import (
    AlertResponse,
    AlertWithAsset,
    AlertListResponse,
    AlertStatsResponse,
    MarkReadRequest,
)

router = APIRouter()


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    unread_only: bool = Query(False, description="Retornar apenas não lidos"),
    severity: str = Query(None, description="Filtrar por severidade"),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    Lista alertas do sistema.
    """
    asset_repo = AssetRepository(session)
    alert_repo = AlertRepository(session)
    
    # Buscar assets para mapear
    assets = await asset_repo.get_all()
    assets_by_id = {a.id: a for a in assets}
    
    # Buscar alertas
    if unread_only:
        alerts = await alert_repo.get_unread(limit=limit)
    elif severity:
        alerts = await alert_repo.get_by_severity(severity, limit=limit)
    else:
        alerts = await alert_repo.get_recent(limit=limit)
    
    # Contar não lidos
    unread_count = await alert_repo.count_unread()
    
    # Montar resposta
    items = []
    for alert in alerts:
        asset = assets_by_id.get(alert.asset_id)
        
        items.append(AlertWithAsset(
            id=alert.id,
            asset_id=alert.asset_id,
            symbol=asset.symbol if asset else "???",
            asset_name=asset.name if asset else "Unknown",
            alert_type=alert.alert_type,
            severity=alert.severity,
            title=alert.title,
            message=alert.message,
            trigger_value=alert.trigger_value,
            trigger_reason=alert.trigger_reason,
            score_at_trigger=alert.score_at_trigger,
            price_at_trigger=alert.price_at_trigger,
            is_read=alert.is_read,
            is_dismissed=alert.is_dismissed,
            read_at=alert.read_at,
            created_at=alert.created_at,
        ))
    
    return AlertListResponse(
        items=items,
        total=len(items),
        unread_count=unread_count,
    )


@router.get("/alerts/stats", response_model=AlertStatsResponse)
async def get_alert_stats(
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna estatísticas de alertas.
    """
    alert_repo = AlertRepository(session)
    
    total = await alert_repo.count()
    unread = await alert_repo.count_unread()
    by_severity = await alert_repo.count_by_severity()
    today = await alert_repo.count_today()
    
    return AlertStatsResponse(
        total=total,
        unread=unread,
        by_severity=by_severity,
        today_count=today,
    )


@router.get("/alerts/{alert_id}", response_model=AlertWithAsset)
async def get_alert(
    alert_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna detalhes de um alerta específico.
    """
    asset_repo = AssetRepository(session)
    alert_repo = AlertRepository(session)
    
    alert = await alert_repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    
    asset = await asset_repo.get_by_id(alert.asset_id)
    
    return AlertWithAsset(
        id=alert.id,
        asset_id=alert.asset_id,
        symbol=asset.symbol if asset else "???",
        asset_name=asset.name if asset else "Unknown",
        alert_type=alert.alert_type,
        severity=alert.severity,
        title=alert.title,
        message=alert.message,
        trigger_value=alert.trigger_value,
        trigger_reason=alert.trigger_reason,
        score_at_trigger=alert.score_at_trigger,
        price_at_trigger=alert.price_at_trigger,
        is_read=alert.is_read,
        is_dismissed=alert.is_dismissed,
        read_at=alert.read_at,
        created_at=alert.created_at,
    )


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Marca um alerta como lido.
    """
    alert_repo = AlertRepository(session)
    
    success = await alert_repo.mark_as_read(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    
    await session.commit()
    return {"message": "Alerta marcado como lido"}


@router.post("/alerts/read-many")
async def mark_alerts_read(
    request: MarkReadRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Marca múltiplos alertas como lidos.
    """
    alert_repo = AlertRepository(session)
    
    count = await alert_repo.mark_many_as_read(request.alert_ids)
    await session.commit()
    
    return {"message": f"{count} alertas marcados como lidos"}


@router.post("/alerts/read-all")
async def mark_all_alerts_read(
    session: AsyncSession = Depends(get_session)
):
    """
    Marca todos alertas como lidos.
    """
    alert_repo = AlertRepository(session)
    
    count = await alert_repo.mark_all_as_read()
    await session.commit()
    
    return {"message": f"{count} alertas marcados como lidos"}


@router.delete("/alerts/{alert_id}")
async def dismiss_alert(
    alert_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Dispensa um alerta.
    """
    alert_repo = AlertRepository(session)
    
    success = await alert_repo.dismiss(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    
    await session.commit()
    return {"message": "Alerta dispensado"}
