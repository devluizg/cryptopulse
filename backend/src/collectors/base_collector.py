"""
Base Collector - Classe abstrata para todos os coletores de dados.

Define a interface padrão e funcionalidades comuns como:
- Rate limiting
- Retry com backoff exponencial
- Logging padronizado
- Métricas de coleta
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypeVar, Generic
import asyncio
import time

import httpx
from loguru import logger

from src.config.settings import settings

T = TypeVar('T')


class CollectorError(Exception):
    """Exceção base para erros de coleta."""
    pass


class RateLimitError(CollectorError):
    """Exceção para quando o rate limit é atingido."""
    pass


class APIError(CollectorError):
    """Exceção para erros de API externa."""
    pass


class CollectorMetrics:
    """Métricas de performance do coletor."""
    
    def __init__(self):
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        self.rate_limit_hits: int = 0
        self.last_request_at: Optional[datetime] = None
        self.last_success_at: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.total_items_collected: int = 0
        self.average_response_time: float = 0.0
        self._response_times: List[float] = []
    
    def record_request(self, success: bool, response_time: float, items: int = 0):
        """Registra uma requisição."""
        self.total_requests += 1
        self.last_request_at = datetime.utcnow()
        self._response_times.append(response_time)
        
        # Manter apenas últimas 100 medições
        if len(self._response_times) > 100:
            self._response_times = self._response_times[-100:]
        
        self.average_response_time = sum(self._response_times) / len(self._response_times)
        
        if success:
            self.successful_requests += 1
            self.last_success_at = datetime.utcnow()
            self.total_items_collected += items
        else:
            self.failed_requests += 1
    
    def record_rate_limit(self):
        """Registra um hit de rate limit."""
        self.rate_limit_hits += 1
    
    def record_error(self, error: str):
        """Registra um erro."""
        self.last_error = error
        self.failed_requests += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna métricas como dicionário."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (
                self.successful_requests / self.total_requests * 100
                if self.total_requests > 0 else 0
            ),
            "rate_limit_hits": self.rate_limit_hits,
            "last_request_at": self.last_request_at.isoformat() if self.last_request_at else None,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None,
            "last_error": self.last_error,
            "total_items_collected": self.total_items_collected,
            "average_response_time_ms": round(self.average_response_time * 1000, 2),
        }


class BaseCollector(ABC, Generic[T]):
    """
    Classe base abstrata para todos os coletores.
    
    Funcionalidades:
    - Cliente HTTP assíncrono com timeout configurável
    - Rate limiting automático
    - Retry com backoff exponencial
    - Logging estruturado
    - Métricas de coleta
    """
    
    # Configurações padrão (podem ser sobrescritas)
    DEFAULT_TIMEOUT: float = 30.0
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_RETRY_DELAY: float = 1.0
    DEFAULT_RATE_LIMIT_DELAY: float = 1.0  # segundos entre requests
    
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        rate_limit_delay: Optional[float] = None,
    ):
        """
        Inicializa o coletor.
        
        Args:
            name: Nome identificador do coletor
            base_url: URL base da API
            api_key: Chave de API (opcional)
            timeout: Timeout para requests (segundos)
            max_retries: Número máximo de tentativas
            rate_limit_delay: Delay entre requests (segundos)
        """
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES
        self.rate_limit_delay = rate_limit_delay or self.DEFAULT_RATE_LIMIT_DELAY
        
        self.metrics = CollectorMetrics()
        self._last_request_time: float = 0
        self._client: Optional[httpx.AsyncClient] = None
        
        self.logger = logger.bind(collector=self.name)
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Retorna o cliente HTTP, criando se necessário."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers=self._get_default_headers(),
            )
        return self._client
    
    async def close(self):
        """Fecha o cliente HTTP."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Retorna headers padrão para requests."""
        headers = {
            "User-Agent": f"CryptoPulse/{settings.app_version}",
            "Accept": "application/json",
        }
        return headers
    
    async def _rate_limit(self):
        """Aplica rate limiting entre requests."""
        now = time.time()
        elapsed = now - self._last_request_time
        
        if elapsed < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - elapsed
            self.logger.debug(f"Rate limiting: aguardando {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        self._last_request_time = time.time()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Executa uma requisição HTTP com retry e rate limiting.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint da API (será concatenado com base_url)
            params: Query parameters
            data: Body da requisição (para POST/PUT)
            headers: Headers adicionais
            
        Returns:
            Resposta da API como dicionário
            
        Raises:
            APIError: Se a requisição falhar após todas as tentativas
            RateLimitError: Se o rate limit da API for atingido
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Rate limiting local
        await self._rate_limit()
        
        last_error: Optional[Exception] = None
        
        for attempt in range(1, self.max_retries + 1):
            start_time = time.time()
            
            try:
                client = await self._get_client()
                
                self.logger.debug(
                    f"Request {attempt}/{self.max_retries}: {method} {url}",
                    params=params
                )
                
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=headers,
                )
                
                response_time = time.time() - start_time
                
                # Verificar rate limit da API
                if response.status_code == 429:
                    self.metrics.record_rate_limit()
                    retry_after = int(response.headers.get("Retry-After", 60))
                    self.logger.warning(
                        f"Rate limit atingido. Aguardando {retry_after}s"
                    )
                    await asyncio.sleep(retry_after)
                    continue
                
                # Verificar erros HTTP
                response.raise_for_status()
                
                # Sucesso
                result = response.json()
                self.metrics.record_request(
                    success=True,
                    response_time=response_time,
                    items=self._count_items(result)
                )
                
                return result
                
            except httpx.HTTPStatusError as e:
                last_error = e
                response_time = time.time() - start_time
                self.metrics.record_request(success=False, response_time=response_time)
                self.metrics.record_error(str(e))
                
                self.logger.warning(
                    f"HTTP Error {e.response.status_code}: {e.response.text[:200]}"
                )
                
                # Não retry para erros 4xx (exceto 429)
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    raise APIError(f"API Error: {e.response.status_code}") from e
                    
            except httpx.TimeoutException as e:
                last_error = e
                self.metrics.record_error(f"Timeout: {str(e)}")
                self.logger.warning(f"Timeout na tentativa {attempt}")
                
            except httpx.RequestError as e:
                last_error = e
                self.metrics.record_error(f"Request Error: {str(e)}")
                self.logger.warning(f"Request error: {str(e)}")
            
            except Exception as e:
                last_error = e
                self.metrics.record_error(f"Unexpected: {str(e)}")
                self.logger.error(f"Erro inesperado: {str(e)}")
            
            # Backoff exponencial
            if attempt < self.max_retries:
                delay = self.DEFAULT_RETRY_DELAY * (2 ** (attempt - 1))
                self.logger.info(f"Retry em {delay}s...")
                await asyncio.sleep(delay)
        
        # Todas as tentativas falharam
        error_msg = f"Falha após {self.max_retries} tentativas: {last_error}"
        self.logger.error(error_msg)
        raise APIError(error_msg) from last_error
    
    def _count_items(self, response: Any) -> int:
        """
        Conta itens na resposta para métricas.
        Pode ser sobrescrito em subclasses.
        """
        if isinstance(response, list):
            return len(response)
        elif isinstance(response, dict):
            # Tentar encontrar array principal na resposta
            for key in ['data', 'items', 'results', 'list']:
                if key in response and isinstance(response[key], list):
                    return len(response[key])
        return 1
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Executa requisição GET."""
        return await self._request("GET", endpoint, params=params, headers=headers)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Executa requisição POST."""
        return await self._request(
            "POST", endpoint, params=params, data=data, headers=headers
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do coletor."""
        return {
            "collector": self.name,
            "base_url": self.base_url,
            "has_api_key": self.api_key is not None,
            **self.metrics.to_dict()
        }
    
    @abstractmethod
    async def collect(self, symbols: Optional[List[str]] = None) -> List[T]:
        """
        Método principal de coleta. Deve ser implementado por subclasses.
        
        Args:
            symbols: Lista de símbolos para coletar (ex: ['BTC', 'ETH'])
            
        Returns:
            Lista de dados coletados (tipo depende da subclasse)
        """
        pass
    
    @abstractmethod
    async def collect_single(self, symbol: str) -> Optional[T]:
        """
        Coleta dados de um único símbolo.
        
        Args:
            symbol: Símbolo do ativo (ex: 'BTC')
            
        Returns:
            Dados coletados ou None se falhar
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica se o coletor está funcionando.
        Pode ser sobrescrito para verificações específicas.
        """
        try:
            # Tenta uma requisição simples
            await self._rate_limit()
            client = await self._get_client()
            response = await client.get(self.base_url)
            
            return {
                "status": "healthy",
                "collector": self.name,
                "base_url": self.base_url,
                "response_status": response.status_code,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "collector": self.name,
                "base_url": self.base_url,
                "error": str(e),
            }
