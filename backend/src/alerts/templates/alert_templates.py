"""
Templates de alertas do CryptoPulse.

Define tipos, severidades e templates de mensagens para todos os alertas.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional


class AlertType(str, Enum):
    """Tipos de alertas suportados."""
    
    # Score Alerts
    SCORE_HIGH = "score_high"
    SCORE_CRITICAL = "score_critical"
    SCORE_SPIKE = "score_spike"
    SCORE_DROP = "score_drop"
    
    # Whale Alerts
    WHALE_LARGE_TX = "whale_large_tx"
    WHALE_ACCUMULATION = "whale_accumulation"
    WHALE_DISTRIBUTION = "whale_distribution"
    
    # Price Alerts
    PRICE_SURGE = "price_surge"
    PRICE_DUMP = "price_dump"
    
    # Volume Alerts
    VOLUME_SPIKE = "volume_spike"
    
    # System Alerts
    SYSTEM_ERROR = "system_error"
    SYSTEM_DATA_DELAY = "system_data_delay"


class AlertSeverity(str, Enum):
    """Níveis de severidade."""
    
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @property
    def priority(self) -> int:
        """Retorna prioridade numérica."""
        return {
            "info": 1,
            "low": 2,
            "medium": 3,
            "high": 4,
            "critical": 5,
        }.get(self.value, 0)
    
    @property
    def color(self) -> str:
        """Retorna cor hex para UI."""
        return {
            "info": "#3B82F6",
            "low": "#10B981",
            "medium": "#F59E0B",
            "high": "#F97316",
            "critical": "#EF4444",
        }.get(self.value, "#6B7280")


@dataclass
class AlertTemplate:
    """Template de configuração de um tipo de alerta."""
    
    alert_type: AlertType
    default_severity: AlertSeverity
    title_template: str
    message_template: str
    cooldown_minutes: int = 30
    enabled: bool = True
    
    def format_title(self, **kwargs) -> str:
        """Formata título com dados."""
        try:
            return self.title_template.format(**kwargs)
        except KeyError:
            return self.title_template
    
    def format_message(self, **kwargs) -> str:
        """Formata mensagem com dados."""
        try:
            return self.message_template.format(**kwargs)
        except KeyError:
            return self.message_template


# === Templates de Alertas ===

ALERT_TEMPLATES: Dict[AlertType, AlertTemplate] = {
    
    # --- Score Alerts ---
    AlertType.SCORE_HIGH: AlertTemplate(
        alert_type=AlertType.SCORE_HIGH,
        default_severity=AlertSeverity.HIGH,
        title_template="🔴 {symbol} entrou em zona de explosão",
        message_template=(
            "{symbol} atingiu score {score:.1f} (zona alta). "
            "Principais fatores: {factors}. "
            "Monitore de perto."
        ),
        cooldown_minutes=60,
    ),
    
    AlertType.SCORE_CRITICAL: AlertTemplate(
        alert_type=AlertType.SCORE_CRITICAL,
        default_severity=AlertSeverity.CRITICAL,
        title_template="🚨 {symbol} em NÍVEL CRÍTICO",
        message_template=(
            "ATENÇÃO: {symbol} atingiu score {score:.1f}! "
            "Condições extremas detectadas. "
            "Alta probabilidade de movimento explosivo."
        ),
        cooldown_minutes=30,
    ),
    
    AlertType.SCORE_SPIKE: AlertTemplate(
        alert_type=AlertType.SCORE_SPIKE,
        default_severity=AlertSeverity.HIGH,
        title_template="📈 {symbol} - Score disparou +{delta:.0f} pontos",
        message_template=(
            "{symbol} subiu {delta:+.1f} pontos em {period}. "
            "Score atual: {score:.1f}. "
            "Mudança rápida indica atividade anormal."
        ),
        cooldown_minutes=30,
    ),
    
    AlertType.SCORE_DROP: AlertTemplate(
        alert_type=AlertType.SCORE_DROP,
        default_severity=AlertSeverity.MEDIUM,
        title_template="📉 {symbol} - Score caiu {delta:.0f} pontos",
        message_template=(
            "{symbol} caiu {delta:.1f} pontos em {period}. "
            "Score atual: {score:.1f}. "
            "Pressão de alta pode estar diminuindo."
        ),
        cooldown_minutes=60,
    ),
    
    # --- Whale Alerts ---
    AlertType.WHALE_LARGE_TX: AlertTemplate(
        alert_type=AlertType.WHALE_LARGE_TX,
        default_severity=AlertSeverity.MEDIUM,
        title_template="🐋 {symbol} - Movimentação de ${amount_display}",
        message_template=(
            "Whale moveu {amount_crypto:.2f} {symbol} (${amount_usd:,.0f}). "
            "Tipo: {tx_type}."
        ),
        cooldown_minutes=5,
    ),
    
    AlertType.WHALE_ACCUMULATION: AlertTemplate(
        alert_type=AlertType.WHALE_ACCUMULATION,
        default_severity=AlertSeverity.HIGH,
        title_template="🐋📈 {symbol} - Whales acumulando",
        message_template=(
            "Padrão de acumulação detectado em {symbol}. "
            "{tx_count} transações nas últimas {hours}h. "
            "Volume: ${total_usd:,.0f}."
        ),
        cooldown_minutes=120,
    ),
    
    AlertType.WHALE_DISTRIBUTION: AlertTemplate(
        alert_type=AlertType.WHALE_DISTRIBUTION,
        default_severity=AlertSeverity.HIGH,
        title_template="🐋📉 {symbol} - Whales distribuindo",
        message_template=(
            "Padrão de distribuição detectado em {symbol}. "
            "{tx_count} transações para exchanges nas últimas {hours}h. "
            "Volume: ${total_usd:,.0f}. Possível pressão de venda."
        ),
        cooldown_minutes=120,
    ),
    
    # --- Price Alerts ---
    AlertType.PRICE_SURGE: AlertTemplate(
        alert_type=AlertType.PRICE_SURGE,
        default_severity=AlertSeverity.MEDIUM,
        title_template="💹 {symbol} subiu {change:+.1f}%",
        message_template=(
            "{symbol} subiu {change:+.1f}% nas últimas {period}. "
            "Preço atual: ${price:,.2f}."
        ),
        cooldown_minutes=60,
    ),
    
    AlertType.PRICE_DUMP: AlertTemplate(
        alert_type=AlertType.PRICE_DUMP,
        default_severity=AlertSeverity.MEDIUM,
        title_template="📉 {symbol} caiu {change:.1f}%",
        message_template=(
            "{symbol} caiu {change:.1f}% nas últimas {period}. "
            "Preço atual: ${price:,.2f}."
        ),
        cooldown_minutes=60,
    ),
    
    # --- Volume Alerts ---
    AlertType.VOLUME_SPIKE: AlertTemplate(
        alert_type=AlertType.VOLUME_SPIKE,
        default_severity=AlertSeverity.MEDIUM,
        title_template="📊 {symbol} - Volume {multiplier:.1f}x acima da média",
        message_template=(
            "{symbol} com volume {multiplier:.1f}x a média. "
            "Picos de volume frequentemente precedem movimentos de preço."
        ),
        cooldown_minutes=60,
    ),
    
    # --- System Alerts ---
    AlertType.SYSTEM_ERROR: AlertTemplate(
        alert_type=AlertType.SYSTEM_ERROR,
        default_severity=AlertSeverity.CRITICAL,
        title_template="❌ Erro: {component}",
        message_template="Erro no componente {component}: {error_message}",
        cooldown_minutes=5,
    ),
    
    AlertType.SYSTEM_DATA_DELAY: AlertTemplate(
        alert_type=AlertType.SYSTEM_DATA_DELAY,
        default_severity=AlertSeverity.LOW,
        title_template="⏳ Atraso na coleta de dados",
        message_template=(
            "Dados de {source} atrasados em {delay_minutes} minutos."
        ),
        cooldown_minutes=30,
    ),
}


def get_template(alert_type: AlertType) -> Optional[AlertTemplate]:
    """Retorna template de um tipo de alerta."""
    return ALERT_TEMPLATES.get(alert_type)
