"""
Middleware de Logging para requisições HTTP.

Fornece:
- Log automático de todas as requisições
- Tracking de request_id
- Métricas de tempo de resposta
- Contexto para logs dentro da requisição
"""

import time
import uuid
from typing import Callable, List, Optional

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from loguru import logger

from src.utils.logger import (
    set_request_context,
    clear_request_context,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que loga todas as requisições HTTP.
    
    Features:
    - Gera request_id único para cada requisição
    - Loga início e fim da requisição
    - Registra tempo de resposta
    - Propaga contexto para logs internos
    """
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[List[str]] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        super().__init__(app)
        self.exclude_paths: List[str] = exclude_paths if exclude_paths is not None else [
            "/health", "/metrics", "/docs", "/redoc", "/openapi.json"
        ]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Verificar se deve ignorar este path
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)
        
        # Gerar request_id
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Definir contexto
        set_request_context(request_id)
        
        # Adicionar ao request state (para uso em handlers)
        request.state.request_id = request_id
        
        # Dados da requisição
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")[:100]
        
        # Log de entrada
        logger.info(
            f"→ {method} {path}",
            request_id=request_id,
            method=method,
            path=path,
            query=query,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        
        # Executar requisição
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calcular duração
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)
            
            # Log de saída
            status_code = response.status_code
            
            # Escolher nível de log baseado no status
            if status_code >= 500:
                log_level = "ERROR"
            elif status_code >= 400:
                log_level = "WARNING"
            else:
                log_level = "INFO"
            
            logger.log(
                log_level,
                f"← {method} {path} | {status_code} | {duration_ms}ms",
                request_id=request_id,
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            
            # Adicionar headers de resposta
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms}ms"
            
            return response
            
        except Exception as e:
            # Log de erro
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)
            
            logger.error(
                f"✗ {method} {path} | ERROR | {duration_ms}ms | {str(e)}",
                request_id=request_id,
                method=method,
                path=path,
                duration_ms=duration_ms,
                error_type=type(e).__name__,
                error_detail=str(e),
            )
            raise
            
        finally:
            # Limpar contexto
            clear_request_context()


class RequestLoggingRoute(APIRoute):
    """
    Custom route class que loga requisições.
    
    Alternativa ao middleware - pode ser usado por router específico.
    
    Uso:
        router = APIRouter(route_class=RequestLoggingRoute)
    """
    
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            # Gerar request_id
            request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
            set_request_context(request_id)
            request.state.request_id = request_id
            
            method = request.method
            path = request.url.path
            
            start_time = time.time()
            
            try:
                logger.debug(f"→ {method} {path}", request_id=request_id)
                
                response = await original_route_handler(request)
                
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.debug(
                    f"← {method} {path} | {response.status_code} | {duration_ms}ms",
                    request_id=request_id,
                )
                
                response.headers["X-Request-ID"] = request_id
                return response
                
            except Exception as e:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.error(
                    f"✗ {method} {path} | ERROR | {duration_ms}ms",
                    request_id=request_id,
                    error_type=type(e).__name__,
                )
                raise
                
            finally:
                clear_request_context()
        
        return custom_route_handler
