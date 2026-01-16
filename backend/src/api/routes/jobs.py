"""
API Routes - Jobs Management.

Endpoints para monitorar e controlar jobs agendados.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.jobs.scheduler import get_scheduler, SchedulerState


router = APIRouter(prefix="/jobs")


# =========================================
# Schemas
# =========================================

class JobRunRequest(BaseModel):
    """Request para executar job."""
    job_id: str


class SchedulerActionResponse(BaseModel):
    """Response de ação no scheduler."""
    success: bool
    message: str
    state: str


# =========================================
# Endpoints - Scheduler
# =========================================

@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    Retorna status completo do scheduler.
    
    Inclui:
    - Estado atual (running, stopped, paused)
    - Tempo de execução
    - Estatísticas globais
    - Status de cada job
    """
    scheduler = await get_scheduler()
    return scheduler.get_status()


@router.post("/scheduler/pause")
async def pause_scheduler():
    """Pausa o scheduler (jobs não executam)."""
    scheduler = await get_scheduler()
    
    if scheduler.state != SchedulerState.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"Scheduler não está rodando (estado: {scheduler.state.value})"
        )
    
    await scheduler.pause()
    
    return SchedulerActionResponse(
        success=True,
        message="Scheduler pausado",
        state=scheduler.state.value,
    )


@router.post("/scheduler/resume")
async def resume_scheduler():
    """Resume o scheduler pausado."""
    scheduler = await get_scheduler()
    
    if scheduler.state != SchedulerState.PAUSED:
        raise HTTPException(
            status_code=400,
            detail=f"Scheduler não está pausado (estado: {scheduler.state.value})"
        )
    
    await scheduler.resume()
    
    return SchedulerActionResponse(
        success=True,
        message="Scheduler resumido",
        state=scheduler.state.value,
    )


# =========================================
# Endpoints - Jobs
# =========================================

@router.get("")
async def list_jobs():
    """
    Lista todos os jobs registrados.
    
    Returns:
        Lista de jobs com status e configuração
    """
    scheduler = await get_scheduler()
    
    jobs = []
    for job_id, job in scheduler._jobs.items():
        config = scheduler._job_configs.get(job_id)
        status = scheduler.get_job_status(job_id)
        
        jobs.append({
            "job_id": job_id,
            "name": config.name if config else job_id,
            "description": config.description if config else "",
            "interval_seconds": config.interval_seconds if config else 0,
            "enabled": config.enabled if config else False,
            "is_running": job.is_running,
            "metrics": status.get("metrics", {}) if status else {},
            "next_run": status.get("next_run") if status else None,
        })
    
    return {
        "scheduler_state": scheduler.state.value,
        "total_jobs": len(jobs),
        "jobs": jobs,
    }


@router.get("/{job_id}")
async def get_job_detail(job_id: str):
    """
    Retorna detalhes de um job específico.
    
    Args:
        job_id: ID do job
        
    Returns:
        Detalhes completos do job incluindo histórico
    """
    scheduler = await get_scheduler()
    
    status = scheduler.get_job_status(job_id)
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Job não encontrado: {job_id}"
        )
    
    # Adiciona histórico
    history = scheduler.get_job_history(job_id, limit=20)
    status["history"] = history
    
    return status


@router.get("/{job_id}/history")
async def get_job_history(
    job_id: str,
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Retorna histórico de execuções de um job.
    
    Args:
        job_id: ID do job
        limit: Número máximo de execuções (1-100)
        
    Returns:
        Lista de execuções recentes
    """
    scheduler = await get_scheduler()
    
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job não encontrado: {job_id}"
        )
    
    history = scheduler.get_job_history(job_id, limit=limit)
    
    return {
        "job_id": job_id,
        "total_in_history": len(history),
        "executions": history,
    }


@router.post("/{job_id}/run")
async def run_job_now(job_id: str):
    """
    Executa um job imediatamente (sob demanda).
    
    Args:
        job_id: ID do job
        
    Returns:
        Resultado da execução
    """
    scheduler = await get_scheduler()
    
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job não encontrado: {job_id}"
        )
    
    if job.is_running:
        raise HTTPException(
            status_code=409,
            detail=f"Job {job_id} já está em execução"
        )
    
    # Executa o job
    result = await scheduler.run_job_now(job_id)
    
    if result is None:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar job {job_id}"
        )
    
    return {
        "job_id": job_id,
        "success": result.success,
        "duration_seconds": round(result.duration_seconds, 2),
        "result_data": result.result_data,
        "error": result.error,
    }


@router.get("/{job_id}/metrics")
async def get_job_metrics(job_id: str):
    """
    Retorna métricas de um job.
    
    Args:
        job_id: ID do job
        
    Returns:
        Métricas acumuladas (execuções, erros, duração média)
    """
    scheduler = await get_scheduler()
    
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job não encontrado: {job_id}"
        )
    
    return {
        "job_id": job_id,
        "metrics": job.metrics.to_dict(),
    }
