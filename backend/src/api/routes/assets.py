"""
CryptoPulse - Asset Routes
Endpoints para gerenciamento de ativos
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.database.connection import get_session
from src.database.repositories import AssetRepository, ScoreRepository
from src.api.schemas import (
    AssetResponse,
    AssetWithScoreResponse,
    AssetListResponse,
    ScoreResponse,
)

router = APIRouter()


@router.get("/assets", response_model=AssetListResponse)
async def list_assets(
    active_only: bool = Query(True, description="Retornar apenas ativos ativos"),
    session: AsyncSession = Depends(get_session)
):
    """
    Lista todos os ativos monitorados com seus scores mais recentes.
    """
    asset_repo = AssetRepository(session)
    score_repo = ScoreRepository(session)
    
    # Buscar ativos
    if active_only:
        assets = await asset_repo.get_active_assets()
    else:
        assets = await asset_repo.get_all()
    
    # Buscar scores mais recentes
    latest_scores = await score_repo.get_all_latest()
    scores_by_asset = {s.asset_id: s for s in latest_scores}
    
    # Montar resposta
    items = []
    for asset in assets:
        score = scores_by_asset.get(asset.id)
        
        asset_data = AssetWithScoreResponse(
            id=asset.id,
            symbol=asset.symbol,
            name=asset.name,
            coingecko_id=asset.coingecko_id,
            binance_symbol=asset.binance_symbol,
            is_active=asset.is_active,
            priority=asset.priority,
            description=asset.description,
            created_at=asset.created_at,
            latest_score=ScoreResponse.model_validate(score) if score else None
        )
        items.append(asset_data)
    
    return AssetListResponse(
        items=items,
        total=len(items)
    )


@router.get("/assets/{symbol}", response_model=AssetWithScoreResponse)
async def get_asset(
    symbol: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna detalhes de um ativo específico com score mais recente.
    """
    asset_repo = AssetRepository(session)
    score_repo = ScoreRepository(session)
    
    # Buscar ativo
    asset = await asset_repo.get_by_symbol(symbol.upper())
    if not asset:
        raise HTTPException(status_code=404, detail=f"Ativo {symbol} não encontrado")
    
    # Buscar score mais recente
    score = await score_repo.get_latest_by_asset(asset.id)
    
    return AssetWithScoreResponse(
        id=asset.id,
        symbol=asset.symbol,
        name=asset.name,
        coingecko_id=asset.coingecko_id,
        binance_symbol=asset.binance_symbol,
        is_active=asset.is_active,
        priority=asset.priority,
        description=asset.description,
        created_at=asset.created_at,
        latest_score=ScoreResponse.model_validate(score) if score else None
    )


@router.get("/assets/{symbol}/scores", response_model=List[ScoreResponse])
async def get_asset_scores(
    symbol: str,
    hours: int = Query(24, ge=1, le=168, description="Horas de histórico"),
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna histórico de scores de um ativo.
    """
    asset_repo = AssetRepository(session)
    score_repo = ScoreRepository(session)
    
    # Buscar ativo
    asset = await asset_repo.get_by_symbol(symbol.upper())
    if not asset:
        raise HTTPException(status_code=404, detail=f"Ativo {symbol} não encontrado")
    
    # Buscar histórico
    scores = await score_repo.get_history(asset.id, hours=hours)
    
    return [ScoreResponse.model_validate(s) for s in scores]


@router.post("/assets/{symbol}/activate")
async def activate_asset(
    symbol: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Ativa monitoramento de um ativo.
    """
    asset_repo = AssetRepository(session)
    
    success = await asset_repo.activate(symbol.upper())
    if not success:
        raise HTTPException(status_code=404, detail=f"Ativo {symbol} não encontrado")
    
    await session.commit()
    return {"message": f"Ativo {symbol} ativado com sucesso"}


@router.post("/assets/{symbol}/deactivate")
async def deactivate_asset(
    symbol: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Desativa monitoramento de um ativo.
    """
    asset_repo = AssetRepository(session)
    
    success = await asset_repo.deactivate(symbol.upper())
    if not success:
        raise HTTPException(status_code=404, detail=f"Ativo {symbol} não encontrado")
    
    await session.commit()
    return {"message": f"Ativo {symbol} desativado com sucesso"}
