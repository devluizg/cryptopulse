"""
CryptoPulse - Sistema de Logs Centralizado

Fornece:
- Configuração centralizada do Loguru
- Rotação automática de arquivos
- Contexto automático (request_id, módulo, etc.)
- Métricas de logs
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Callable, List
from functools import wraps
import asyncio
from contextvars import ContextVar

from loguru import logger


# ============================================
# Context Variables (para request tracking)
# ============================================
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


# ============================================
# Métricas de Logs
# ============================================
class LogMetrics:
    """Rastreia métricas dos logs."""
    
    def __init__(self):
        self.counts: Dict[str, int] = {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0,
        }
        self.last_error: Optional[str] = None
        self.last_error_time: Optional[datetime] = None
        self.errors_last_hour: int = 0
        self._error_timestamps: List[datetime] = []
    
    def record(self, level: str) -> None:
        """Registra um log."""
        level_upper = level.upper()
        if level_upper in self.counts:
            self.counts[level_upper] += 1
        
        if level_upper in ("ERROR", "CRITICAL"):
            now = datetime.utcnow()
            self._error_timestamps.append(now)
            self.last_error_time = now
            
            # Limpar timestamps antigos (mais de 1 hora)
            cutoff = now - timedelta(hours=1)
            self._error_timestamps = [
                ts for ts in self._error_timestamps if ts > cutoff
            ]
            self.errors_last_hour = len(self._error_timestamps)
    
    def set_last_error(self, message: str) -> None:
        """Define última mensagem de erro."""
        self.last_error = message[:500]
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna métricas como dict."""
        return {
            "counts": self.counts.copy(),
            "total": sum(self.counts.values()),
            "errors_last_hour": self.errors_last_hour,
            "last_error": self.last_error,
            "last_error_time": (
                self.last_error_time.isoformat() 
                if self.last_error_time else None
            ),
        }
    
    def reset(self) -> None:
        """Reseta contadores."""
        for key in self.counts:
            self.counts[key] = 0
        self.errors_last_hour = 0
        self._error_timestamps = []


# Instância global de métricas
log_metrics = LogMetrics()


# ============================================
# Formatos de Log (strings)
# ============================================
# Formato para console (colorido)
CONSOLE_FORMAT = (
    "<green>{time:HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Formato para arquivo (texto simples com timestamp completo)
FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} - "
    "{message}"
)


# ============================================
# Sink de Métricas
# ============================================
def metrics_sink(message) -> None:
    """Sink que registra métricas."""
    record = message.record
    log_metrics.record(record["level"].name)
    
    if record["level"].name in ("ERROR", "CRITICAL"):
        log_metrics.set_last_error(str(record["message"]))


# ============================================
# Configuração Principal
# ============================================
class LoggerConfig:
    """Gerencia configuração do logger."""
    
    def __init__(self):
        self._configured = False
        self._handlers: List[int] = []
        self._log_dir: Optional[Path] = None
    
    def setup(
        self,
        level: str = "INFO",
        log_dir: Optional[str] = None,
        json_logs: bool = False,
        enable_file: bool = True,
        app_name: str = "cryptopulse",
    ) -> None:
        """
        Configura o sistema de logs.
        
        Args:
            level: Nível mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Diretório para arquivos de log
            json_logs: Se True, usa formato simplificado no console
            enable_file: Se True, salva logs em arquivo
            app_name: Nome da aplicação (usado no nome dos arquivos)
        """
        # Remover handlers existentes
        logger.remove()
        self._handlers.clear()
        
        # Determinar diretório de logs
        if log_dir:
            self._log_dir = Path(log_dir)
        else:
            # Usar backend/logs por padrão
            self._log_dir = Path(__file__).parent.parent.parent / "logs"
        
        # Criar diretório se não existe
        if enable_file:
            self._log_dir.mkdir(parents=True, exist_ok=True)
        
        # ========================================
        # Handler 1: Console
        # ========================================
        handler_id = logger.add(
            sys.stdout,
            format=CONSOLE_FORMAT,
            level=level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
        self._handlers.append(handler_id)
        
        # ========================================
        # Handler 2: Arquivo principal (com rotação)
        # ========================================
        if enable_file and self._log_dir:
            main_log_file = self._log_dir / f"{app_name}.log"
            handler_id = logger.add(
                str(main_log_file),
                format=FILE_FORMAT,
                level=level,
                rotation="10 MB",
                retention="7 days",
                compression="gz",
                backtrace=True,
                diagnose=True,
                enqueue=True,
            )
            self._handlers.append(handler_id)
        
        # ========================================
        # Handler 3: Arquivo de erros (separado)
        # ========================================
        if enable_file and self._log_dir:
            error_log_file = self._log_dir / f"{app_name}_errors.log"
            handler_id = logger.add(
                str(error_log_file),
                format=FILE_FORMAT,
                level="ERROR",
                rotation="5 MB",
                retention="30 days",
                compression="gz",
                backtrace=True,
                diagnose=True,
                enqueue=True,
            )
            self._handlers.append(handler_id)
        
        # ========================================
        # Handler 4: Métricas (sempre ativo)
        # ========================================
        handler_id = logger.add(
            metrics_sink,
            level="DEBUG",
        )
        self._handlers.append(handler_id)
        
        self._configured = True
        
        logger.info(
            f"Logger configurado: level={level}, "
            f"log_dir={self._log_dir}, json={json_logs}"
        )
    
    def get_log_dir(self) -> Optional[Path]:
        """Retorna diretório de logs."""
        return self._log_dir
    
    @property
    def is_configured(self) -> bool:
        """Retorna se o logger foi configurado."""
        return self._configured


# Instância global de configuração
logger_config = LoggerConfig()


# ============================================
# Funções de Conveniência
# ============================================
def setup_logging(
    level: str = "INFO",
    log_dir: Optional[str] = None,
    json_logs: bool = False,
    enable_file: bool = True,
) -> None:
    """
    Função de conveniência para configurar logs.
    
    Uso:
        from src.utils.logger import setup_logging
        setup_logging(level="DEBUG", enable_file=True)
    """
    logger_config.setup(
        level=level,
        log_dir=log_dir,
        json_logs=json_logs,
        enable_file=enable_file,
    )


def get_logger(name: Optional[str] = None, **context):
    """
    Retorna logger com contexto.
    
    Uso:
        log = get_logger("meu_modulo", asset="BTC")
        log.info("Processando...")
    """
    bound_logger = logger.bind(**context)
    if name:
        bound_logger = bound_logger.bind(module=name)
    return bound_logger


def get_log_metrics() -> Dict[str, Any]:
    """Retorna métricas dos logs."""
    return log_metrics.to_dict()


def set_request_context(request_id: str, user_id: Optional[str] = None) -> None:
    """Define contexto da requisição atual."""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)


def clear_request_context() -> None:
    """Limpa contexto da requisição."""
    request_id_var.set(None)
    user_id_var.set(None)


# ============================================
# Decorators
# ============================================
def log_function(
    level: str = "DEBUG",
    log_args: bool = True,
    log_result: bool = False,
    log_time: bool = True,
):
    """
    Decorator para logar execução de funções.
    
    Uso:
        @log_function(level="INFO", log_time=True)
        def minha_funcao(x, y):
            return x + y
    """
    def decorator(func: Callable):
        func_name = func.__name__
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            if log_args:
                logger.log(level, f"[{func_name}] Iniciando | args={args}, kwargs={kwargs}")
            else:
                logger.log(level, f"[{func_name}] Iniciando")
            
            try:
                result = func(*args, **kwargs)
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                msg = f"[{func_name}] Concluído"
                if log_time:
                    msg += f" | duration={duration:.3f}s"
                if log_result:
                    msg += f" | result={result}"
                
                logger.log(level, msg)
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error(f"[{func_name}] Erro após {duration:.3f}s: {e}")
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            if log_args:
                logger.log(level, f"[{func_name}] Iniciando | args={args}, kwargs={kwargs}")
            else:
                logger.log(level, f"[{func_name}] Iniciando")
            
            try:
                result = await func(*args, **kwargs)
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                msg = f"[{func_name}] Concluído"
                if log_time:
                    msg += f" | duration={duration:.3f}s"
                if log_result:
                    msg += f" | result={result}"
                
                logger.log(level, msg)
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error(f"[{func_name}] Erro após {duration:.3f}s: {e}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def log_async_function(
    level: str = "DEBUG",
    log_args: bool = False,
    log_result: bool = False,
    log_time: bool = True,
):
    """Alias para log_function (funciona com async também)."""
    return log_function(
        level=level,
        log_args=log_args,
        log_result=log_result,
        log_time=log_time,
    )


# ============================================
# Exports
# ============================================
__all__ = [
    "logger",
    "setup_logging",
    "logger_config",
    "LoggerConfig",
    "get_logger",
    "get_log_metrics",
    "log_metrics",
    "set_request_context",
    "clear_request_context",
    "request_id_var",
    "user_id_var",
    "log_function",
    "log_async_function",
]
