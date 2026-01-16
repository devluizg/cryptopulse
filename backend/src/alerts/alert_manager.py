"""
Gerenciador central do sistema de alertas.

Coordena detecção, criação, persistência e envio de alertas.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .templates import AlertType, AlertSeverity
from .threshold_monitor import ThresholdMonitor, AlertCandidate
from .channels import (
    NotificationPayload,
    push_channel,
    email_channel,
    webhook_channel,
)
from ..database.connection import async_session_maker
from ..database.repositories import AlertRepository, AssetRepository, ScoreRepository


class AlertManager:
    """
    Gerenciador central de alertas.
    
    Responsabilidades:
    - Coordenar verificação de thresholds
    - Persistir alertas no banco
    - Distribuir notificações pelos canais
    - Gerenciar ciclo de vida dos alertas
    """
    
    def __init__(self):
        self.monitor = ThresholdMonitor()
        self._is_running = False
        self._process_count = 0
        self._created_alerts = 0
        self._sent_notifications = 0
    
    async def process_score(
        self,
        asset_id: int,
        symbol: str,
        score: float,
        indicator_scores: Optional[Dict[str, float]] = None,
        score_history: Optional[List[Dict]] = None,
    ) -> List[int]:
        """
        Processa um score e gera alertas se necessário.
        
        Args:
            asset_id: ID do ativo
            symbol: Símbolo do ativo
            score: Score atual
            indicator_scores: Scores dos indicadores
            score_history: Histórico de scores
            
        Returns:
            Lista de IDs dos alertas criados
        """
        self._process_count += 1
        created_ids = []
        
        # Verifica condições de score
        candidates = await self.monitor.check_score(
            asset_id=asset_id,
            symbol=symbol,
            current_score=score,
            indicator_scores=indicator_scores,
            score_history=score_history,
        )
        
        # Cria alertas para cada candidato
        for candidate in candidates:
            alert_id = await self._create_and_send(candidate)
            if alert_id:
                created_ids.append(alert_id)
        
        return created_ids
    
    async def process_whale_transaction(
        self,
        asset_id: int,
        symbol: str,
        amount_usd: float,
        amount_crypto: float,
        tx_type: str,
    ) -> Optional[int]:
        """
        Processa transação de whale e gera alerta se necessário.
        
        Returns:
            ID do alerta criado ou None
        """
        candidate = await self.monitor.check_whale_transaction(
            asset_id=asset_id,
            symbol=symbol,
            amount_usd=amount_usd,
            amount_crypto=amount_crypto,
            tx_type=tx_type,
        )
        
        if candidate:
            return await self._create_and_send(candidate)
        
        return None
    
    async def process_price_change(
        self,
        asset_id: int,
        symbol: str,
        change_percent: float,
        current_price: float,
        period: str = "24h",
    ) -> Optional[int]:
        """
        Processa mudança de preço e gera alerta se necessário.
        
        Returns:
            ID do alerta criado ou None
        """
        candidate = await self.monitor.check_price_change(
            asset_id=asset_id,
            symbol=symbol,
            change_percent=change_percent,
            current_price=current_price,
            period=period,
        )
        
        if candidate:
            return await self._create_and_send(candidate)
        
        return None
    
    async def process_volume_spike(
        self,
        asset_id: int,
        symbol: str,
        current_volume: float,
        avg_volume: float,
    ) -> Optional[int]:
        """
        Processa pico de volume e gera alerta se necessário.
        
        Returns:
            ID do alerta criado ou None
        """
        candidate = await self.monitor.check_volume_spike(
            asset_id=asset_id,
            symbol=symbol,
            current_volume=current_volume,
            avg_volume=avg_volume,
        )
        
        if candidate:
            return await self._create_and_send(candidate)
        
        return None
    
    async def _create_and_send(self, candidate: AlertCandidate) -> Optional[int]:
        """
        Cria alerta no banco e envia notificações.
        
        Args:
            candidate: Candidato a alerta
            
        Returns:
            ID do alerta criado ou None
        """
        try:
            async with async_session_maker() as session:
                repo = AlertRepository(session)
                
                # Extrai valores do data para os campos corretos
                trigger_value = candidate.data.get("score") or candidate.data.get("amount_usd")
                score_at_trigger = candidate.data.get("score")
                price_at_trigger = candidate.data.get("current_price")
                
                # Cria no banco
                alert = await repo.create_alert(
                    asset_id=candidate.asset_id,
                    alert_type=candidate.alert_type.value,
                    severity=candidate.severity.value,
                    title=candidate.title,
                    message=candidate.message,
                    trigger_value=trigger_value,
                    trigger_reason=candidate.data,
                    score_at_trigger=score_at_trigger,
                    price_at_trigger=price_at_trigger,
                )
                
                await session.commit()
                
                self._created_alerts += 1
                logger.info(
                    f"Alert created: [{candidate.severity.value.upper()}] "
                    f"{candidate.symbol} - {candidate.alert_type.value}"
                )
                
                # Envia notificações
                await self._send_notifications(alert, candidate)
                
                return alert.id
                
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return None
    
    async def _send_notifications(
        self,
        alert,
        candidate: AlertCandidate,
    ):
        """
        Envia notificações para todos os canais.
        
        Args:
            alert: Alerta do banco
            candidate: Candidato original
        """
        payload = NotificationPayload(
            alert_id=alert.id,
            alert_type=candidate.alert_type.value,
            severity=candidate.severity.value,
            title=candidate.title,
            message=candidate.message,
            symbol=candidate.symbol,
            asset_id=candidate.asset_id,
            data=candidate.data,
            created_at=alert.created_at,
        )
        
        # Envia para cada canal
        channels = [
            push_channel,
            webhook_channel,
        ]
        
        # Email só para alertas críticos
        if candidate.severity == AlertSeverity.CRITICAL:
            channels.append(email_channel)
        
        for channel in channels:
            try:
                success = await channel.send(payload)
                if success:
                    self._sent_notifications += 1
            except Exception as e:
                logger.error(f"Channel {channel.name} failed: {e}")
    
    async def create_system_alert(
        self,
        component: str,
        error_message: str,
        severity: AlertSeverity = AlertSeverity.HIGH,
    ) -> Optional[int]:
        """
        Cria alerta de sistema.
        
        Args:
            component: Nome do componente com erro
            error_message: Mensagem de erro
            severity: Severidade do alerta
            
        Returns:
            ID do alerta ou None
        """
        candidate = AlertCandidate(
            alert_type=AlertType.SYSTEM_ERROR,
            severity=severity,
            title=f"❌ Erro: {component}",
            message=f"Erro no componente {component}: {error_message}",
            asset_id=0,  # Sistema
            symbol="SYSTEM",
            data={
                "component": component,
                "error": error_message,
            },
        )
        
        return await self._create_and_send(candidate)
    
    async def run_check_cycle(self) -> Dict[str, Any]:
        """
        Executa um ciclo completo de verificação.
        
        Verifica todos os ativos ativos e gera alertas.
        
        Returns:
            Resumo do ciclo
        """
        start_time = datetime.utcnow()
        alerts_created: List[int] = []
        assets_count = 0
        
        try:
            async with async_session_maker() as session:
                asset_repo = AssetRepository(session)
                score_repo = ScoreRepository(session)
                
                # Busca ativos ativos
                assets = await asset_repo.get_active_assets()
                assets_count = len(assets)
                
                for asset in assets:
                    # Busca score mais recente
                    latest_score = await score_repo.get_latest_by_asset(asset.id)
                    
                    if not latest_score:
                        continue
                    
                    # Busca histórico
                    history = await score_repo.get_history(
                        asset_id=asset.id,
                        hours=24,
                        limit=50,
                    )
                    
                    # Converte histórico para dict
                    history_dicts = [
                        {
                            "explosion_score": s.explosion_score,
                            "calculated_at": s.calculated_at,
                        }
                        for s in history
                    ]
                    
                    # Converte indicator scores
                    indicator_scores = {
                        "whale_accumulation": latest_score.whale_accumulation_score,
                        "exchange_netflow": latest_score.exchange_netflow_score,
                        "volume_anomaly": latest_score.volume_anomaly_score,
                        "oi_pressure": latest_score.oi_pressure_score,
                        "narrative_momentum": latest_score.narrative_momentum_score,
                    }
                    
                    # Processa score
                    created = await self.process_score(
                        asset_id=asset.id,
                        symbol=asset.symbol,
                        score=latest_score.explosion_score,
                        indicator_scores=indicator_scores,
                        score_history=history_dicts,
                    )
                    
                    alerts_created.extend(created)
                    
                    # Verifica preço se disponível
                    if latest_score.price_change_24h:
                        price_alert = await self.process_price_change(
                            asset_id=asset.id,
                            symbol=asset.symbol,
                            change_percent=latest_score.price_change_24h,
                            current_price=latest_score.price_usd or 0,
                        )
                        if price_alert:
                            alerts_created.append(price_alert)
        
        except Exception as e:
            logger.error(f"Check cycle failed: {e}")
            await self.create_system_alert(
                component="AlertManager",
                error_message=str(e),
            )
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "duration_seconds": duration,
            "assets_checked": assets_count,
            "alerts_created": len(alerts_created),
            "alert_ids": alerts_created,
        }
    
    async def cleanup_old_alerts(self, days: int = 30) -> int:
        """
        Remove alertas antigos.
        
        Args:
            days: Remover alertas mais antigos que X dias
            
        Returns:
            Número de alertas removidos
        """
        try:
            async with async_session_maker() as session:
                repo = AlertRepository(session)
                deleted = await repo.delete_old(days=days)
                await session.commit()
                
                logger.info(f"Cleaned up {deleted} old alerts")
                return deleted
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do manager."""
        return {
            "process_count": self._process_count,
            "created_alerts": self._created_alerts,
            "sent_notifications": self._sent_notifications,
            "monitor_stats": self.monitor.get_stats(),
            "channels": {
                "push": push_channel.get_stats(),
                "email": email_channel.get_stats(),
                "webhook": webhook_channel.get_stats(),
            },
        }


# Instância global
alert_manager = AlertManager()
