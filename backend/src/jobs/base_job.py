"""
Base Job - Classe abstrata para todos os jobs.

Fornece:
- Estrutura padrão de execução
- Logging consistente
- Métricas de execução
- Tratamento de erros
- Retry automático
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
import asyncio
import traceback

from loguru import logger

from src.config.jobs_config import JobConfig, JobPriority


@dataclass
class JobResult:
    """Resultado de uma execução de job."""
    
    job_id: str
    success: bool
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    result_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    retry_count: int = 0
    
    @property
    def is_error(self) -> bool:
        return not self.success or self.error is not None


@dataclass
class JobMetrics:
    """Métricas acumuladas de um job."""
    
    job_id: str
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_duration_seconds: float = 0.0
    last_run: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100
    
    @property
    def avg_duration_seconds(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return self.total_duration_seconds / self.total_runs
    
    def record_success(self, duration: float):
        """Registra execução bem-sucedida."""
        self.total_runs += 1
        self.successful_runs += 1
        self.total_duration_seconds += duration
        self.last_run = datetime.utcnow()
        self.last_success = datetime.utcnow()
        self.consecutive_failures = 0
    
    def record_failure(self, duration: float, error: str):
        """Registra execução com falha."""
        self.total_runs += 1
        self.failed_runs += 1
        self.total_duration_seconds += duration
        self.last_run = datetime.utcnow()
        self.last_failure = datetime.utcnow()
        self.last_error = error
        self.consecutive_failures += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "job_id": self.job_id,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "success_rate": f"{self.success_rate:.1f}%",
            "avg_duration_seconds": round(self.avg_duration_seconds, 2),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "last_error": self.last_error,
            "consecutive_failures": self.consecutive_failures,
        }


class BaseJob(ABC):
    """
    Classe base abstrata para todos os jobs do sistema.
    
    Implementa:
    - Ciclo de vida padronizado (setup -> execute -> cleanup)
    - Logging automático
    - Métricas de execução
    - Retry com backoff
    - Timeout handling
    """
    
    def __init__(self, config: JobConfig):
        """
        Inicializa o job.
        
        Args:
            config: Configuração do job
        """
        self.config = config
        self.job_id = config.job_id
        self.name = config.name
        self.logger = logger.bind(job=self.job_id)
        
        # Estado
        self._is_running = False
        self._should_stop = False
        self._current_task: Optional[asyncio.Task] = None
        
        # Métricas
        self.metrics = JobMetrics(job_id=self.job_id)
        
        # Histórico de execuções (últimas N)
        self._history: List[JobResult] = []
        self._max_history = 100
    
    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """
        Executa a lógica principal do job.
        
        DEVE ser implementado pelas subclasses.
        
        Returns:
            Dict com dados do resultado
        """
        pass
    
    async def setup(self) -> None:
        """
        Executado antes do execute().
        Pode ser sobrescrito para inicialização.
        """
        pass
    
    async def cleanup(self) -> None:
        """
        Executado após o execute() (sucesso ou falha).
        Pode ser sobrescrito para limpeza.
        """
        pass
    
    async def on_success(self, result: JobResult) -> None:
        """
        Callback executado após sucesso.
        Pode ser sobrescrito.
        """
        pass
    
    async def on_failure(self, result: JobResult) -> None:
        """
        Callback executado após falha.
        Pode ser sobrescrito.
        """
        pass
    
    async def run(self) -> JobResult:
        """
        Executa o job completo com todo o ciclo de vida.
        
        Fluxo:
        1. Verificações pré-execução
        2. Setup
        3. Execute (com timeout)
        4. Cleanup
        5. Callbacks
        6. Retorna resultado
        
        Returns:
            JobResult com detalhes da execução
        """
        started_at = datetime.utcnow()
        result_data: Dict[str, Any] = {}
        error: Optional[str] = None
        error_traceback: Optional[str] = None
        retry_count = 0
        
        # Verifica se já está rodando
        if self._is_running:
            self.logger.warning(f"Job {self.job_id} já está em execução, ignorando")
            return JobResult(
                job_id=self.job_id,
                success=False,
                started_at=started_at,
                finished_at=datetime.utcnow(),
                duration_seconds=0,
                error="Job já em execução",
            )
        
        self._is_running = True
        self._should_stop = False
        
        try:
            # Setup
            await self.setup()
            
            # Execute com retry
            for attempt in range(self.config.max_retries + 1):
                retry_count = attempt
                
                try:
                    # Execute com timeout
                    result_data = await asyncio.wait_for(
                        self.execute(),
                        timeout=self.config.timeout_seconds,
                    )
                    
                    # Sucesso - sai do loop de retry
                    error = None
                    error_traceback = None
                    break
                    
                except asyncio.TimeoutError:
                    error = f"Timeout após {self.config.timeout_seconds}s"
                    error_traceback = None
                    self.logger.error(f"[{self.job_id}] {error}")
                    
                except asyncio.CancelledError:
                    error = "Job cancelado"
                    error_traceback = None
                    self.logger.warning(f"[{self.job_id}] {error}")
                    break  # Não faz retry em cancelamento
                    
                except Exception as e:
                    error = str(e)
                    error_traceback = traceback.format_exc()
                    self.logger.error(f"[{self.job_id}] Erro: {error}")
                
                # Se não é a última tentativa, espera e tenta de novo
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay_seconds * (attempt + 1)
                    self.logger.info(f"[{self.job_id}] Retry {attempt + 1}/{self.config.max_retries} em {delay}s")
                    await asyncio.sleep(delay)
        
        finally:
            # Cleanup sempre executa
            try:
                await self.cleanup()
            except Exception as e:
                self.logger.error(f"[{self.job_id}] Erro no cleanup: {e}")
            
            self._is_running = False
        
        # Monta resultado
        finished_at = datetime.utcnow()
        duration = (finished_at - started_at).total_seconds()
        success = error is None
        
        result = JobResult(
            job_id=self.job_id,
            success=success,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration,
            result_data=result_data,
            error=error,
            error_traceback=error_traceback,
            retry_count=retry_count,
        )
        
        # Atualiza métricas
        if success:
            self.metrics.record_success(duration)
            self.logger.info(f"[{self.job_id}] ✅ Concluído em {duration:.2f}s")
        else:
            self.metrics.record_failure(duration, error or "Unknown error")
            self.logger.error(f"[{self.job_id}] ❌ Falhou após {duration:.2f}s: {error}")
        
        # Adiciona ao histórico
        self._add_to_history(result)
        
        # Callbacks
        try:
            if success:
                await self.on_success(result)
            else:
                await self.on_failure(result)
        except Exception as e:
            self.logger.error(f"[{self.job_id}] Erro no callback: {e}")
        
        return result
    
    def _add_to_history(self, result: JobResult) -> None:
        """Adiciona resultado ao histórico."""
        self._history.append(result)
        
        # Limita tamanho do histórico
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
    
    def stop(self) -> None:
        """Sinaliza para o job parar."""
        self._should_stop = True
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
    
    @property
    def is_running(self) -> bool:
        """Retorna se o job está em execução."""
        return self._is_running
    
    @property
    def should_stop(self) -> bool:
        """Retorna se o job deve parar."""
        return self._should_stop
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do job."""
        return {
            "job_id": self.job_id,
            "name": self.name,
            "enabled": self.config.enabled,
            "is_running": self._is_running,
            "interval_seconds": self.config.interval_seconds,
            "metrics": self.metrics.to_dict(),
        }
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna histórico de execuções."""
        history = self._history[-limit:]
        return [
            {
                "job_id": r.job_id,
                "success": r.success,
                "started_at": r.started_at.isoformat(),
                "finished_at": r.finished_at.isoformat(),
                "duration_seconds": round(r.duration_seconds, 2),
                "error": r.error,
                "retry_count": r.retry_count,
            }
            for r in reversed(history)
        ]
