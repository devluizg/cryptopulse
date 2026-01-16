"""
CryptoPulse Alert System Package

Sistema de alertas que detecta condições anormais no mercado
e notifica os usuários sobre potenciais oportunidades ou riscos.

Componentes:
- templates: Tipos de alertas e templates de mensagens
- channels: Canais de notificação (push, email, webhook)
- threshold_monitor: Monitor de thresholds
- alert_manager: Gerenciador central
"""

from .templates import (
    AlertType,
    AlertSeverity,
    AlertTemplate,
    ALERT_TEMPLATES,
    get_template,
)
from .threshold_monitor import ThresholdMonitor, AlertCandidate
from .alert_manager import AlertManager, alert_manager
from .channels import (
    NotificationPayload,
    push_channel,
    email_channel,
    webhook_channel,
)

__all__ = [
    # Templates
    "AlertType",
    "AlertSeverity",
    "AlertTemplate",
    "ALERT_TEMPLATES",
    "get_template",
    # Monitor
    "ThresholdMonitor",
    "AlertCandidate",
    # Manager
    "AlertManager",
    "alert_manager",
    # Channels
    "NotificationPayload",
    "push_channel",
    "email_channel",
    "webhook_channel",
]
