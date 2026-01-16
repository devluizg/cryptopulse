"""
CryptoPulse - Signal Routes
Endpoints para scores e sinais
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone

from src.database.connection import get_session
from src.database.repositories import AssetRepository, ScoreRepository
from src.api.schemas import (
    ScoreDetail,
    ScoreWithAsset,
    ScoreHistoryResponse,
    DashboardResponse,
)

router = APIRouter()


@router.get("/signals/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna dados para o dashboard principal.
    Inclui todos os ativos com seus scores mais recentes.
    """
    asset_repo = AssetRepository(session)
    score_repo = ScoreRepository(session)
    
    # Buscar ativos ativos
    assets = await asset_repo.get_active_assets()
    assets_by_id = {a.id: a for a in assets}
    
    # Buscar scores mais recentes
    scores = await score_repo.get_all_latest()
    
    # Contadores
    high_count = 0
    attention_count = 0
    low_count = 0
    
    # Montar lista de scores com assets
    items = []
    for score in scores:
        asset = assets_by_id.get(score.asset_id)
        if not asset:
            continue
        
        # Contar por status
        if score.status == "high":
            high_count += 1
        elif score.status == "attention":
            attention_count += 1
        else:
            low_count += 1
        
        items.append(ScoreWithAsset(
            id=score.id,
            asset_id=score.asset_id,
            symbol=asset.symbol,
            asset_name=asset.name,
            explosion_score=score.explosion_score,
            status=score.status,
            whale_accumulation_score=score.whale_accumulation_score,
            exchange_netflow_score=score.exchange_netflow_score,
            volume_anomaly_score=score.volume_anomaly_score,
            oi_pressure_score=score.oi_pressure_score,
            narrative_momentum_score=score.narrative_momentum_score,
            price_usd=score.price_usd,
            price_change_24h=score.price_change_24h,
            volume_24h=score.volume_24h,
            calculation_details=score.calculation_details,
            main_drivers=score.main_drivers,
            calculated_at=score.calculated_at,
        ))
    
    # Ordenar por score decrescente
    items.sort(key=lambda x: x.explosion_score, reverse=True)
    
    return DashboardResponse(
        total_assets=len(assets),
        high_count=high_count,
        attention_count=attention_count,
        low_count=low_count,
        assets=items,
        updated_at=datetime.now(timezone.utc),
    )


@router.get("/signals/high", response_model=List[ScoreWithAsset])
async def get_high_signals(
    threshold: float = Query(70.0, ge=0, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna ativos com score acima do threshold (zona de explosão).
    """
    asset_repo = AssetRepository(session)
    score_repo = ScoreRepository(session)
    
    # Buscar assets para mapear
    assets = await asset_repo.get_active_assets()
    assets_by_id = {a.id: a for a in assets}
    
    # Buscar scores altos
    scores = await score_repo.get_high_scores(threshold=threshold)
    
    items = []
    seen_assets = set()
    
    for score in scores:
        # Pegar apenas o mais recente de cada ativo
        if score.asset_id in seen_assets:
            continue
        seen_assets.add(score.asset_id)
        
        asset = assets_by_id.get(score.asset_id)
        if not asset:
            continue
        
        items.append(ScoreWithAsset(
            id=score.id,
            asset_id=score.asset_id,
            symbol=asset.symbol,
            asset_name=asset.name,
            explosion_score=score.explosion_score,
            status=score.status,
            whale_accumulation_score=score.whale_accumulation_score,
            exchange_netflow_score=score.exchange_netflow_score,
            volume_anomaly_score=score.volume_anomaly_score,
            oi_pressure_score=score.oi_pressure_score,
            narrative_momentum_score=score.narrative_momentum_score,
            price_usd=score.price_usd,
            price_change_24h=score.price_change_24h,
            volume_24h=score.volume_24h,
            calculation_details=score.calculation_details,
            main_drivers=score.main_drivers,
            calculated_at=score.calculated_at,
        ))
    
    return items


@router.get("/signals/{symbol}", response_model=ScoreDetail)
async def get_signal_detail(
    symbol: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna detalhes do score mais recente de um ativo.
    """
    score_repo = ScoreRepository(session)
    
    score = await score_repo.get_latest_by_symbol(symbol.upper())
    if not score:
        raise HTTPException(
            status_code=404, 
            detail=f"Nenhum score encontrado para {symbol}"
        )
    
    return ScoreDetail.model_validate(score)


@router.get("/signals/{symbol}/history", response_model=ScoreHistoryResponse)
async def get_signal_history(
    symbol: str,
    hours: int = Query(24, ge=1, le=168),
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna histórico de scores de um ativo.
    """
    asset_repo = AssetRepository(session)
    score_repo = ScoreRepository(session)
    
    # Verificar se ativo existe
    asset = await asset_repo.get_by_symbol(symbol.upper())
    if not asset:
        raise HTTPException(status_code=404, detail=f"Ativo {symbol} não encontrado")
    
    # Buscar histórico
    scores = await score_repo.get_history(asset.id, hours=hours)
    
    return ScoreHistoryResponse(
        symbol=symbol.upper(),
        scores=[ScoreDetail.model_validate(s) for s in scores],
        count=len(scores),
    )
