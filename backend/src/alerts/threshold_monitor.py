"""
Monitor de thresholds para geração de alertas.

Verifica condições e gera alertas quando thresholds são ultrapassados.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from loguru import logger

from .templates import AlertType, AlertSeverity, ALERT_TEMPLATES, AlertTemplate


@dataclass
class ThresholdConfig:
    """Configuração de threshold para um tipo de alerta."""
    
    alert_type: AlertType
    threshold: float
    comparison: str = "gte"  # gte, lte, gt, lt, eq
    cooldown_minutes: int = 30
    enabled: bool = True


@dataclass
class AlertCandidate:
    """Candidato a alerta gerado pelo monitor."""
    
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    asset_id: int
    symbol: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "asset_id": self.asset_id,
            "symbol": self.symbol,
            "data": self.data,
        }


def get_template_safe(alert_type: AlertType) -> AlertTemplate:
    """Retorna template ou um template padrão se não existir."""
    template = ALERT_TEMPLATES.get(alert_type)
    if template is None:
        # Retorna template padrão
        return AlertTemplate(
            alert_type=alert_type,
            default_severity=AlertSeverity.MEDIUM,
            title_template="{symbol} - Alert",
            message_template="Alert triggered for {symbol}",
            cooldown_minutes=30,
        )
    return template


class ThresholdMonitor:
    """
    Monitor de thresholds para detecção de condições de alerta.
    
    Responsabilidades:
    - Verificar se scores ultrapassaram thresholds
    - Detectar mudanças rápidas (spikes/drops)
    - Detectar transações grandes de whales
    - Gerenciar cooldowns para evitar spam
    """
    
    # Thresholds padrão
    SCORE_HIGH_THRESHOLD = 70.0
    SCORE_CRITICAL_THRESHOLD = 85.0
    SCORE_SPIKE_DELTA = 15.0
    SCORE_DROP_DELTA = -15.0
    WHALE_MIN_USD = 5_000_000
    VOLUME_SPIKE_MULTIPLIER = 3.0
    PRICE_SURGE_PERCENT = 10.0
    PRICE_DUMP_PERCENT = -10.0
    
    def __init__(self):
        self._cooldowns: Dict[str, datetime] = {}
        self._last_scores: Dict[str, float] = {}
        self._check_count = 0
        self._alert_count = 0
    
    def _get_cooldown_key(self, alert_type: AlertType, symbol: str) -> str:
        """Gera chave única para cooldown."""
        return f"{alert_type.value}:{symbol}"
    
    def _is_in_cooldown(self, alert_type: AlertType, symbol: str) -> bool:
        """Verifica se alerta está em cooldown."""
        key = self._get_cooldown_key(alert_type, symbol)
        
        if key not in self._cooldowns:
            return False
        
        template = get_template_safe(alert_type)
        cooldown_minutes = template.cooldown_minutes
        
        expiry = self._cooldowns[key] + timedelta(minutes=cooldown_minutes)
        return datetime.utcnow() < expiry
    
    def _set_cooldown(self, alert_type: AlertType, symbol: str):
        """Define cooldown para um alerta."""
        key = self._get_cooldown_key(alert_type, symbol)
        self._cooldowns[key] = datetime.utcnow()
    
    def _get_top_factors(self, indicator_scores: Dict[str, float]) -> str:
        """Retorna os principais fatores do score."""
        if not indicator_scores:
            return "dados insuficientes"
        
        factor_names = {
            "whale_accumulation": "Whales",
            "exchange_netflow": "Netflow",
            "volume_anomaly": "Volume",
            "oi_pressure": "OI",
            "narrative_momentum": "Narrativa",
        }
        
        sorted_factors = sorted(
            indicator_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:2]
        
        return ", ".join(
            f"{factor_names.get(k, k)} ({v:.0f})"
            for k, v in sorted_factors
        )
    
    async def check_score(
        self,
        asset_id: int,
        symbol: str,
        current_score: float,
        indicator_scores: Optional[Dict[str, float]] = None,
        score_history: Optional[List[Dict]] = None,
    ) -> List[AlertCandidate]:
        """
        Verifica condições de score e retorna alertas.
        
        Args:
            asset_id: ID do ativo
            symbol: Símbolo do ativo
            current_score: Score atual
            indicator_scores: Scores individuais dos indicadores
            score_history: Histórico de scores
            
        Returns:
            Lista de alertas candidatos
        """
        self._check_count += 1
        alerts: List[AlertCandidate] = []
        indicator_scores = indicator_scores or {}
        
        # Recupera score anterior
        previous_score = self._last_scores.get(symbol, current_score)
        self._last_scores[symbol] = current_score
        
        # 1. Score Critical (>85)
        if current_score >= self.SCORE_CRITICAL_THRESHOLD:
            if not self._is_in_cooldown(AlertType.SCORE_CRITICAL, symbol):
                template = get_template_safe(AlertType.SCORE_CRITICAL)
                alerts.append(AlertCandidate(
                    alert_type=AlertType.SCORE_CRITICAL,
                    severity=AlertSeverity.CRITICAL,
                    title=template.format_title(symbol=symbol),
                    message=template.format_message(
                        symbol=symbol,
                        score=current_score,
                    ),
                    asset_id=asset_id,
                    symbol=symbol,
                    data={
                        "score": current_score,
                        "threshold": self.SCORE_CRITICAL_THRESHOLD,
                        "indicator_scores": indicator_scores,
                    },
                ))
                self._set_cooldown(AlertType.SCORE_CRITICAL, symbol)
        
        # 2. Score High (>70) - só se não é critical
        elif current_score >= self.SCORE_HIGH_THRESHOLD:
            entered_zone = previous_score < self.SCORE_HIGH_THRESHOLD
            if entered_zone and not self._is_in_cooldown(AlertType.SCORE_HIGH, symbol):
                template = get_template_safe(AlertType.SCORE_HIGH)
                factors = self._get_top_factors(indicator_scores)
                alerts.append(AlertCandidate(
                    alert_type=AlertType.SCORE_HIGH,
                    severity=AlertSeverity.HIGH,
                    title=template.format_title(symbol=symbol),
                    message=template.format_message(
                        symbol=symbol,
                        score=current_score,
                        factors=factors,
                    ),
                    asset_id=asset_id,
                    symbol=symbol,
                    data={
                        "score": current_score,
                        "previous_score": previous_score,
                        "threshold": self.SCORE_HIGH_THRESHOLD,
                        "indicator_scores": indicator_scores,
                    },
                ))
                self._set_cooldown(AlertType.SCORE_HIGH, symbol)
        
        # 3. Score Spike (subiu muito rápido)
        delta = current_score - previous_score
        if delta >= self.SCORE_SPIKE_DELTA:
            if not self._is_in_cooldown(AlertType.SCORE_SPIKE, symbol):
                template = get_template_safe(AlertType.SCORE_SPIKE)
                alerts.append(AlertCandidate(
                    alert_type=AlertType.SCORE_SPIKE,
                    severity=AlertSeverity.HIGH,
                    title=template.format_title(symbol=symbol, delta=delta),
                    message=template.format_message(
                        symbol=symbol,
                        delta=delta,
                        period="última verificação",
                        score=current_score,
                    ),
                    asset_id=asset_id,
                    symbol=symbol,
                    data={
                        "score": current_score,
                        "previous_score": previous_score,
                        "delta": delta,
                    },
                ))
                self._set_cooldown(AlertType.SCORE_SPIKE, symbol)
        
        # 4. Score Drop (caiu muito rápido)
        elif delta <= self.SCORE_DROP_DELTA:
            if not self._is_in_cooldown(AlertType.SCORE_DROP, symbol):
                template = get_template_safe(AlertType.SCORE_DROP)
                alerts.append(AlertCandidate(
                    alert_type=AlertType.SCORE_DROP,
                    severity=AlertSeverity.MEDIUM,
                    title=template.format_title(symbol=symbol, delta=abs(delta)),
                    message=template.format_message(
                        symbol=symbol,
                        delta=abs(delta),
                        period="última verificação",
                        score=current_score,
                    ),
                    asset_id=asset_id,
                    symbol=symbol,
                    data={
                        "score": current_score,
                        "previous_score": previous_score,
                        "delta": delta,
                    },
                ))
                self._set_cooldown(AlertType.SCORE_DROP, symbol)
        
        self._alert_count += len(alerts)
        return alerts
    
    async def check_whale_transaction(
        self,
        asset_id: int,
        symbol: str,
        amount_usd: float,
        amount_crypto: float,
        tx_type: str,
    ) -> Optional[AlertCandidate]:
        """
        Verifica se transação de whale deve gerar alerta.
        
        Args:
            asset_id: ID do ativo
            symbol: Símbolo
            amount_usd: Valor em USD
            amount_crypto: Quantidade em crypto
            tx_type: Tipo da transação
            
        Returns:
            AlertCandidate ou None
        """
        if amount_usd < self.WHALE_MIN_USD:
            return None
        
        if self._is_in_cooldown(AlertType.WHALE_LARGE_TX, symbol):
            return None
        
        # Formata valor para display
        if amount_usd >= 1_000_000_000:
            amount_display = f"{amount_usd/1_000_000_000:.1f}B"
        elif amount_usd >= 1_000_000:
            amount_display = f"{amount_usd/1_000_000:.1f}M"
        else:
            amount_display = f"{amount_usd/1_000:.0f}K"
        
        # Determina severidade pelo valor
        if amount_usd >= 50_000_000:
            severity = AlertSeverity.CRITICAL
        elif amount_usd >= 20_000_000:
            severity = AlertSeverity.HIGH
        elif amount_usd >= 10_000_000:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        template = get_template_safe(AlertType.WHALE_LARGE_TX)
        
        alert = AlertCandidate(
            alert_type=AlertType.WHALE_LARGE_TX,
            severity=severity,
            title=template.format_title(
                symbol=symbol,
                amount_display=amount_display,
            ),
            message=template.format_message(
                symbol=symbol,
                amount_crypto=amount_crypto,
                amount_usd=amount_usd,
                tx_type=tx_type,
            ),
            asset_id=asset_id,
            symbol=symbol,
            data={
                "amount_usd": amount_usd,
                "amount_crypto": amount_crypto,
                "tx_type": tx_type,
            },
        )
        
        self._set_cooldown(AlertType.WHALE_LARGE_TX, symbol)
        self._alert_count += 1
        
        return alert
    
    async def check_price_change(
        self,
        asset_id: int,
        symbol: str,
        change_percent: float,
        current_price: float,
        period: str = "24h",
    ) -> Optional[AlertCandidate]:
        """
        Verifica mudança de preço.
        
        Args:
            asset_id: ID do ativo
            symbol: Símbolo
            change_percent: Mudança percentual
            current_price: Preço atual
            period: Período da mudança
            
        Returns:
            AlertCandidate ou None
        """
        # Price Surge
        if change_percent >= self.PRICE_SURGE_PERCENT:
            alert_type = AlertType.PRICE_SURGE
            if self._is_in_cooldown(alert_type, symbol):
                return None
            
            template = get_template_safe(alert_type)
            alert = AlertCandidate(
                alert_type=alert_type,
                severity=AlertSeverity.MEDIUM,
                title=template.format_title(
                    symbol=symbol,
                    change=change_percent,
                ),
                message=template.format_message(
                    symbol=symbol,
                    change=change_percent,
                    period=period,
                    price=current_price,
                ),
                asset_id=asset_id,
                symbol=symbol,
                data={
                    "change_percent": change_percent,
                    "current_price": current_price,
                    "period": period,
                },
            )
            self._set_cooldown(alert_type, symbol)
            self._alert_count += 1
            return alert
        
        # Price Dump
        elif change_percent <= self.PRICE_DUMP_PERCENT:
            alert_type = AlertType.PRICE_DUMP
            if self._is_in_cooldown(alert_type, symbol):
                return None
            
            template = get_template_safe(alert_type)
            alert = AlertCandidate(
                alert_type=alert_type,
                severity=AlertSeverity.MEDIUM,
                title=template.format_title(
                    symbol=symbol,
                    change=abs(change_percent),
                ),
                message=template.format_message(
                    symbol=symbol,
                    change=abs(change_percent),
                    period=period,
                    price=current_price,
                ),
                asset_id=asset_id,
                symbol=symbol,
                data={
                    "change_percent": change_percent,
                    "current_price": current_price,
                    "period": period,
                },
            )
            self._set_cooldown(alert_type, symbol)
            self._alert_count += 1
            return alert
        
        return None
    
    async def check_volume_spike(
        self,
        asset_id: int,
        symbol: str,
        current_volume: float,
        avg_volume: float,
    ) -> Optional[AlertCandidate]:
        """
        Verifica pico de volume.
        
        Args:
            asset_id: ID do ativo
            symbol: Símbolo
            current_volume: Volume atual
            avg_volume: Volume médio
            
        Returns:
            AlertCandidate ou None
        """
        if avg_volume <= 0:
            return None
        
        multiplier = current_volume / avg_volume
        
        if multiplier < self.VOLUME_SPIKE_MULTIPLIER:
            return None
        
        if self._is_in_cooldown(AlertType.VOLUME_SPIKE, symbol):
            return None
        
        template = get_template_safe(AlertType.VOLUME_SPIKE)
        
        alert = AlertCandidate(
            alert_type=AlertType.VOLUME_SPIKE,
            severity=AlertSeverity.MEDIUM,
            title=template.format_title(
                symbol=symbol,
                multiplier=multiplier,
            ),
            message=template.format_message(
                symbol=symbol,
                multiplier=multiplier,
            ),
            asset_id=asset_id,
            symbol=symbol,
            data={
                "current_volume": current_volume,
                "avg_volume": avg_volume,
                "multiplier": multiplier,
            },
        )
        
        self._set_cooldown(AlertType.VOLUME_SPIKE, symbol)
        self._alert_count += 1
        
        return alert
    
    def clear_cooldowns(self):
        """Limpa todos os cooldowns."""
        self._cooldowns.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do monitor."""
        return {
            "check_count": self._check_count,
            "alert_count": self._alert_count,
            "active_cooldowns": len(self._cooldowns),
            "tracked_symbols": len(self._last_scores),
        }
