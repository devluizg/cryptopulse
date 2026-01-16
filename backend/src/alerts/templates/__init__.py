"""Alert Templates Package."""

from .alert_templates import (
    AlertType,
    AlertSeverity,
    AlertTemplate,
    ALERT_TEMPLATES,
    get_template,
)

__all__ = [
    "AlertType",
    "AlertSeverity",
    "AlertTemplate",
    "ALERT_TEMPLATES",
    "get_template",
]
