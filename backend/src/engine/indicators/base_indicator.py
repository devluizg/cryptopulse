"""
Classe base abstrata para todos os indicadores.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
import numpy as np


class BaseIndicator(ABC):
    """
    Classe base para todos os indicadores do sistema.
    
    Cada indicador:
    - Recebe dados brutos (do collector ou banco)
    - Processa e normaliza os dados
    - Retorna um score de 0-100
    
    Score interpretation:
    - 0-30: Baixa atividade / bearish
    - 30-50: Atividade normal
    - 50-70: Atividade elevada / atenção
    - 70-100: Atividade extrema / bullish forte
    """
    
    # Limites padrão para normalização
    SCORE_MIN = 0.0
    SCORE_MAX = 100.0
    
    def __init__(self, name: str, weight: float = 1.0):
        """
        Inicializa o indicador.
        
        Args:
            name: Nome do indicador
            weight: Peso no cálculo final (0.0 a 1.0)
        """
        self.name = name
        self.weight = min(max(weight, 0.0), 1.0)  # Clamp entre 0 e 1
        self._last_calculation: Optional[datetime] = None
        self._last_score: Optional[float] = None
        self._last_raw_data: Optional[Dict] = None
        self._last_details: Optional[Dict] = None
    
    @abstractmethod
    async def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calcula o score do indicador.
        
        Args:
            data: Dados necessários para o cálculo
            
        Returns:
            Score de 0 a 100
        """
        pass
    
    @abstractmethod
    async def calculate_with_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula o score e retorna detalhes do cálculo.
        
        Args:
            data: Dados necessários para o cálculo
            
        Returns:
            Dict com 'score' e 'details'
        """
        pass
    
    def normalize_score(self, value: float, min_val: float = 0, max_val: float = 100) -> float:
        """
        Normaliza um valor para a escala 0-100.
        
        Args:
            value: Valor a normalizar
            min_val: Valor mínimo esperado
            max_val: Valor máximo esperado
            
        Returns:
            Valor normalizado entre 0 e 100
        """
        if max_val == min_val:
            return 50.0
        
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return self.clamp_score(normalized)
    
    def clamp_score(self, score: float) -> float:
        """
        Limita o score entre 0 e 100.
        
        Args:
            score: Score a limitar
            
        Returns:
            Score limitado
        """
        return float(min(max(score, self.SCORE_MIN), self.SCORE_MAX))
    
    def calculate_z_score(self, value: float, values: List[float]) -> float:
        """
        Calcula o Z-score de um valor em relação a uma série.
        
        Args:
            value: Valor atual
            values: Lista de valores históricos
            
        Returns:
            Z-score (desvios padrão da média)
        """
        if not values or len(values) < 2:
            return 0.0
        
        arr = np.array(values)
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        
        if std == 0:
            return 0.0
        
        return float((value - mean) / std)
    
    def z_score_to_percentile(self, z_score: float) -> float:
        """
        Converte Z-score para percentil (0-100).
        
        Args:
            z_score: Z-score
            
        Returns:
            Percentil aproximado
        """
        # Aproximação usando função logística
        # Z-score de -3 a +3 mapeado para 0-100
        percentile = float(100 / (1 + np.exp(-z_score)))
        return self.clamp_score(percentile)
    
    def weighted_average(self, values: List[float], weights: List[float]) -> float:
        """
        Calcula média ponderada.
        
        Args:
            values: Lista de valores
            weights: Lista de pesos
            
        Returns:
            Média ponderada
        """
        if not values or not weights:
            return 0.0
        
        if len(values) != len(weights):
            logger.warning(f"[{self.name}] Tamanhos diferentes: values={len(values)}, weights={len(weights)}")
            return float(np.mean(values))
        
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        
        return float(sum(v * w for v, w in zip(values, weights)) / total_weight)
    
    def exponential_decay_weights(self, count: int, decay: float = 0.9) -> List[float]:
        """
        Gera pesos com decaimento exponencial (mais recente = maior peso).
        
        Args:
            count: Quantidade de pesos
            decay: Fator de decaimento (0-1)
            
        Returns:
            Lista de pesos
        """
        if count <= 0:
            return []
        
        weights = [decay ** i for i in range(count)]
        weights.reverse()  # Mais recente primeiro
        return weights
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna status atual do indicador.
        
        Returns:
            Dict com informações de status
        """
        return {
            "name": self.name,
            "weight": self.weight,
            "last_score": self._last_score,
            "last_calculation": self._last_calculation.isoformat() if self._last_calculation else None,
            "last_details": self._last_details,
        }
    
    def _update_state(self, score: float, raw_data: Dict, details: Dict):
        """
        Atualiza estado interno após cálculo.
        
        Args:
            score: Score calculado
            raw_data: Dados brutos usados
            details: Detalhes do cálculo
        """
        self._last_calculation = datetime.utcnow()
        self._last_score = score
        self._last_raw_data = raw_data
        self._last_details = details
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, weight={self.weight})>"
