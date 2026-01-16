"""
Calculadora principal do Explosion Score.

Combina todos os indicadores para gerar o score final.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .indicators import (
    BaseIndicator,
    WhaleIndicator,
    VolumeIndicator,
    OpenInterestIndicator,
    NarrativeIndicator,
    NetflowIndicator,
)
from ..config.constants import (
    SCORE_THRESHOLD_HIGH,
    SCORE_THRESHOLD_ATTENTION,
    INDICATOR_WEIGHTS,
)


class ScoreCalculator:
    """
    Calculadora do Explosion Score.
    
    Combina múltiplos indicadores com pesos configuráveis:
    - Whale Accumulation (25%)
    - Exchange Netflow (25%)
    - Volume Anomaly (20%)
    - Open Interest Pressure (15%)
    - Narrative Momentum (15%)
    
    Score final de 0-100:
    - 0-40: Low (mercado calmo)
    - 40-70: Attention (atividade crescente)
    - 70-100: High (potencial explosão)
    """
    
    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        """
        Inicializa o calculador.
        
        Args:
            custom_weights: Pesos customizados (opcional)
        """
        # Usar pesos customizados ou padrão
        weights = custom_weights or INDICATOR_WEIGHTS
        
        # Inicializar indicadores
        self.indicators: Dict[str, BaseIndicator] = {
            "whale": WhaleIndicator(weight=weights.get("whale_accumulation", 0.25)),
            "netflow": NetflowIndicator(weight=weights.get("exchange_netflow", 0.25)),
            "volume": VolumeIndicator(weight=weights.get("volume_anomaly", 0.20)),
            "oi": OpenInterestIndicator(weight=weights.get("oi_pressure", 0.15)),
            "narrative": NarrativeIndicator(weight=weights.get("narrative_momentum", 0.15)),
        }
        
        self._last_calculation: Optional[datetime] = None
        self._calculation_count = 0
    
    async def calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula o Explosion Score completo.
        
        Args:
            data: {
                "asset_symbol": str,
                "whale_data": Dict,      # Dados para WhaleIndicator
                "netflow_data": Dict,    # Dados para NetflowIndicator
                "volume_data": Dict,     # Dados para VolumeIndicator
                "oi_data": Dict,         # Dados para OpenInterestIndicator
                "narrative_data": Dict,  # Dados para NarrativeIndicator
            }
            
        Returns:
            {
                "explosion_score": float,
                "status": str,
                "indicator_scores": Dict,
                "indicator_details": Dict,
                "calculated_at": datetime,
                "asset_symbol": str,
            }
        """
        asset_symbol = data.get("asset_symbol", "UNKNOWN")
        
        logger.info(f"[ScoreCalculator] Calculando score para {asset_symbol}")
        
        # Calcular cada indicador
        indicator_scores = {}
        indicator_details = {}
        weighted_sum = 0.0
        total_weight = 0.0
        
        # 1. Whale Indicator
        whale_data = data.get("whale_data", {})
        whale_data["asset_symbol"] = asset_symbol
        try:
            whale_result = await self.indicators["whale"].calculate_with_details(whale_data)
            indicator_scores["whale_accumulation"] = whale_result["score"]
            indicator_details["whale_accumulation"] = whale_result["details"]
            weighted_sum += whale_result["score"] * self.indicators["whale"].weight
            total_weight += self.indicators["whale"].weight
        except Exception as e:
            logger.error(f"[ScoreCalculator] Erro no WhaleIndicator: {e}")
            indicator_scores["whale_accumulation"] = 50.0
            indicator_details["whale_accumulation"] = {"error": str(e)}
        
        # 2. Netflow Indicator
        netflow_data = data.get("netflow_data", {})
        netflow_data["asset_symbol"] = asset_symbol
        try:
            netflow_result = await self.indicators["netflow"].calculate_with_details(netflow_data)
            indicator_scores["exchange_netflow"] = netflow_result["score"]
            indicator_details["exchange_netflow"] = netflow_result["details"]
            weighted_sum += netflow_result["score"] * self.indicators["netflow"].weight
            total_weight += self.indicators["netflow"].weight
        except Exception as e:
            logger.error(f"[ScoreCalculator] Erro no NetflowIndicator: {e}")
            indicator_scores["exchange_netflow"] = 50.0
            indicator_details["exchange_netflow"] = {"error": str(e)}
        
        # 3. Volume Indicator
        volume_data = data.get("volume_data", {})
        volume_data["asset_symbol"] = asset_symbol
        try:
            volume_result = await self.indicators["volume"].calculate_with_details(volume_data)
            indicator_scores["volume_anomaly"] = volume_result["score"]
            indicator_details["volume_anomaly"] = volume_result["details"]
            weighted_sum += volume_result["score"] * self.indicators["volume"].weight
            total_weight += self.indicators["volume"].weight
        except Exception as e:
            logger.error(f"[ScoreCalculator] Erro no VolumeIndicator: {e}")
            indicator_scores["volume_anomaly"] = 50.0
            indicator_details["volume_anomaly"] = {"error": str(e)}
        
        # 4. Open Interest Indicator
        oi_data = data.get("oi_data", {})
        oi_data["asset_symbol"] = asset_symbol
        try:
            oi_result = await self.indicators["oi"].calculate_with_details(oi_data)
            indicator_scores["oi_pressure"] = oi_result["score"]
            indicator_details["oi_pressure"] = oi_result["details"]
            weighted_sum += oi_result["score"] * self.indicators["oi"].weight
            total_weight += self.indicators["oi"].weight
        except Exception as e:
            logger.error(f"[ScoreCalculator] Erro no OpenInterestIndicator: {e}")
            indicator_scores["oi_pressure"] = 50.0
            indicator_details["oi_pressure"] = {"error": str(e)}
        
        # 5. Narrative Indicator
        narrative_data = data.get("narrative_data", {})
        narrative_data["asset_symbol"] = asset_symbol
        try:
            narrative_result = await self.indicators["narrative"].calculate_with_details(narrative_data)
            indicator_scores["narrative_momentum"] = narrative_result["score"]
            indicator_details["narrative_momentum"] = narrative_result["details"]
            weighted_sum += narrative_result["score"] * self.indicators["narrative"].weight
            total_weight += self.indicators["narrative"].weight
        except Exception as e:
            logger.error(f"[ScoreCalculator] Erro no NarrativeIndicator: {e}")
            indicator_scores["narrative_momentum"] = 50.0
            indicator_details["narrative_momentum"] = {"error": str(e)}
        
        # Calcular score final
        if total_weight > 0:
            explosion_score = weighted_sum / total_weight
        else:
            explosion_score = 50.0
        
        # Clamp entre 0 e 100
        explosion_score = min(max(explosion_score, 0), 100)
        
        # Determinar status
        status = self._determine_status(explosion_score)
        
        # Gerar resumo
        summary = self._generate_summary(explosion_score, indicator_scores, status)
        
        # Atualizar estado
        self._last_calculation = datetime.utcnow()
        self._calculation_count += 1
        
        result = {
            "explosion_score": round(explosion_score, 2),
            "status": status,
            "indicator_scores": {k: round(v, 2) for k, v in indicator_scores.items()},
            "indicator_details": indicator_details,
            "weights": {
                "whale_accumulation": self.indicators["whale"].weight,
                "exchange_netflow": self.indicators["netflow"].weight,
                "volume_anomaly": self.indicators["volume"].weight,
                "oi_pressure": self.indicators["oi"].weight,
                "narrative_momentum": self.indicators["narrative"].weight,
            },
            "summary": summary,
            "calculated_at": self._last_calculation,
            "asset_symbol": asset_symbol,
        }
        
        logger.info(
            f"[ScoreCalculator] {asset_symbol}: "
            f"score={explosion_score:.1f}, status={status}"
        )
        
        return result
    
    async def calculate_quick(self, data: Dict[str, Any]) -> float:
        """
        Calcula apenas o score final (sem detalhes).
        
        Útil para cálculos em batch.
        """
        result = await self.calculate(data)
        return result["explosion_score"]
    
    def _determine_status(self, score: float) -> str:
        """
        Determina o status baseado no score.
        
        Args:
            score: Explosion Score (0-100)
            
        Returns:
            'high', 'attention', ou 'low'
        """
        if score >= SCORE_THRESHOLD_HIGH:
            return "high"
        elif score >= SCORE_THRESHOLD_ATTENTION:
            return "attention"
        else:
            return "low"
    
    def _generate_summary(
        self, 
        score: float, 
        indicator_scores: Dict[str, float],
        status: str
    ) -> str:
        """
        Gera um resumo textual do score.
        """
        # Encontrar indicadores mais relevantes
        sorted_indicators = sorted(
            indicator_scores.items(), 
            key=lambda x: abs(x[1] - 50), 
            reverse=True
        )
        
        top_bullish = [
            (k, v) for k, v in sorted_indicators 
            if v >= 60
        ][:2]
        
        top_bearish = [
            (k, v) for k, v in sorted_indicators 
            if v <= 40
        ][:2]
        
        parts = []
        
        if status == "high":
            parts.append(f"⚠️ ALERTA: Score em zona de explosão ({score:.0f})")
        elif status == "attention":
            parts.append(f"📊 Score em zona de atenção ({score:.0f})")
        else:
            parts.append(f"✅ Score em zona normal ({score:.0f})")
        
        if top_bullish:
            bullish_names = [self._indicator_name(k) for k, v in top_bullish]
            parts.append(f"Sinais positivos: {', '.join(bullish_names)}")
        
        if top_bearish:
            bearish_names = [self._indicator_name(k) for k, v in top_bearish]
            parts.append(f"Sinais negativos: {', '.join(bearish_names)}")
        
        return " | ".join(parts)
    
    def _indicator_name(self, key: str) -> str:
        """Retorna nome amigável do indicador."""
        names = {
            "whale_accumulation": "Whales",
            "exchange_netflow": "Netflow",
            "volume_anomaly": "Volume",
            "oi_pressure": "OI",
            "narrative_momentum": "Narrativa",
        }
        return names.get(key, key)
    
    def get_indicator_status(self) -> Dict[str, Any]:
        """Retorna status de todos os indicadores."""
        return {
            name: indicator.get_status()
            for name, indicator in self.indicators.items()
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Atualiza os pesos dos indicadores.
        
        Args:
            new_weights: Dict com novos pesos
        """
        for key, weight in new_weights.items():
            if key in ["whale", "whale_accumulation"]:
                self.indicators["whale"].weight = weight
            elif key in ["netflow", "exchange_netflow"]:
                self.indicators["netflow"].weight = weight
            elif key in ["volume", "volume_anomaly"]:
                self.indicators["volume"].weight = weight
            elif key in ["oi", "oi_pressure"]:
                self.indicators["oi"].weight = weight
            elif key in ["narrative", "narrative_momentum"]:
                self.indicators["narrative"].weight = weight
        
        logger.info(f"[ScoreCalculator] Pesos atualizados: {new_weights}")
