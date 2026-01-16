"""
Indicador de anomalia de volume.

Analisa:
- Volume atual vs média histórica
- Desvio padrão do volume
- Picos de volume (Z-score)
- Tendência de volume (crescente/decrescente)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import numpy as np

from .base_indicator import BaseIndicator


class VolumeIndicator(BaseIndicator):
    """
    Calcula score baseado em anomalias de volume.
    
    Sinais bullish (score alto):
    - Volume significativamente acima da média (Z-score > 2)
    - Volume crescente nas últimas horas
    - Breakout de volume com preço subindo
    
    Sinais bearish (score baixo):
    - Volume muito baixo (mercado sem interesse)
    - Volume caindo consistentemente
    """
    
    # Configurações
    LOOKBACK_PERIODS = 24  # Períodos para média/std
    Z_SCORE_THRESHOLD_HIGH = 2.0  # Z-score para considerar anomalia
    Z_SCORE_THRESHOLD_EXTREME = 3.0  # Z-score para anomalia extrema
    
    # Pesos internos
    WEIGHT_ZSCORE = 0.40
    WEIGHT_TREND = 0.30
    WEIGHT_RELATIVE = 0.30
    
    def __init__(self, weight: float = 0.20):
        """
        Inicializa o indicador de volume.
        
        Args:
            weight: Peso no score final (padrão 20%)
        """
        super().__init__(name="volume_anomaly", weight=weight)
    
    async def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calcula o score de anomalia de volume.
        
        Args:
            data: {
                "current_volume": float,  # Volume atual (24h ou período)
                "historical_volumes": List[float],  # Volumes históricos
                "price_change_percent": float,  # Mudança de preço %
                "asset_symbol": str,
            }
            
        Returns:
            Score de 0 a 100
        """
        result = await self.calculate_with_details(data)
        return result["score"]
    
    async def calculate_with_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula score com detalhes completos.
        """
        current_volume = data.get("current_volume", 0)
        historical_volumes = data.get("historical_volumes", [])
        price_change = data.get("price_change_percent", 0)
        asset_symbol = data.get("asset_symbol", "UNKNOWN")
        
        # Se não há dados históricos suficientes
        if len(historical_volumes) < 3:
            details = {
                "current_volume": current_volume,
                "historical_count": len(historical_volumes),
                "z_score": None,
                "volume_vs_avg": None,
                "trend": "unknown",
                "sub_scores": {
                    "zscore_score": 50,
                    "trend_score": 50,
                    "relative_score": 50,
                },
                "reason": "Dados históricos insuficientes"
            }
            self._update_state(50.0, data, details)
            return {"score": 50.0, "details": details}
        
        # Calcular estatísticas
        volumes_array = np.array(historical_volumes)
        mean_volume = np.mean(volumes_array)
        std_volume = np.std(volumes_array)
        
        # Z-score do volume atual
        if std_volume > 0:
            z_score = (current_volume - mean_volume) / std_volume
        else:
            z_score = 0
        
        # Ratio vs média
        volume_ratio = current_volume / mean_volume if mean_volume > 0 else 1
        
        # Tendência (últimos N períodos)
        trend = self._calculate_trend(historical_volumes)
        
        # === SUB-SCORES ===
        
        # 1. Z-Score Score
        zscore_score = self._zscore_to_score(z_score)
        
        # 2. Trend Score
        trend_score = self._trend_to_score(trend, price_change)
        
        # 3. Relative Volume Score
        relative_score = self._relative_to_score(volume_ratio)
        
        # === SCORE FINAL ===
        final_score = (
            zscore_score * self.WEIGHT_ZSCORE +
            trend_score * self.WEIGHT_TREND +
            relative_score * self.WEIGHT_RELATIVE
        )
        final_score = self.clamp_score(final_score)
        
        # Ajuste: volume alto com preço subindo é mais bullish
        if z_score > 1.5 and price_change > 2:
            final_score = min(100, final_score + 10)
        
        # Detalhes
        details = {
            "current_volume": current_volume,
            "mean_volume": mean_volume,
            "std_volume": std_volume,
            "z_score": round(z_score, 2),
            "volume_vs_avg": round(volume_ratio, 2),
            "trend": trend["direction"],
            "trend_strength": round(trend["strength"], 2),
            "price_change_percent": price_change,
            "sub_scores": {
                "zscore_score": round(zscore_score, 2),
                "trend_score": round(trend_score, 2),
                "relative_score": round(relative_score, 2),
            },
            "anomaly_detected": bool(z_score >= self.Z_SCORE_THRESHOLD_HIGH),
            "reason": self._generate_reason(z_score, trend, volume_ratio)
        }
        
        self._update_state(final_score, data, details)
        
        logger.debug(
            f"[{self.name}] {asset_symbol}: score={final_score:.1f}, "
            f"z={z_score:.2f}, ratio={volume_ratio:.2f}x, trend={trend['direction']}"
        )
        
        return {"score": final_score, "details": details}
    
    def _zscore_to_score(self, z_score: float) -> float:
        """
        Converte Z-score para score 0-100.
        
        Z-score > 2: Volume muito alto (bullish) -> 70-90
        Z-score 1-2: Volume acima da média -> 55-70
        Z-score -1 a 1: Volume normal -> 40-55
        Z-score < -1: Volume baixo -> 30-40
        Z-score < -2: Volume muito baixo -> 20-30
        """
        if z_score >= self.Z_SCORE_THRESHOLD_EXTREME:
            # Volume extremamente alto
            return min(95, 80 + (z_score - 3) * 5)
        elif z_score >= self.Z_SCORE_THRESHOLD_HIGH:
            # Volume muito alto
            return 70 + (z_score - 2) * 10
        elif z_score >= 1:
            # Volume acima da média
            return 55 + (z_score - 1) * 15
        elif z_score >= -1:
            # Volume normal
            return 45 + z_score * 10
        elif z_score >= -2:
            # Volume baixo
            return 30 + (z_score + 2) * 7.5
        else:
            # Volume muito baixo
            return max(15, 30 + (z_score + 2) * 7.5)
    
    def _calculate_trend(self, volumes: List[float]) -> Dict[str, Any]:
        """
        Calcula tendência do volume.
        
        Returns:
            Dict com direction (up/down/flat) e strength (0-1)
        """
        if len(volumes) < 4:
            return {"direction": "unknown", "strength": 0}
        
        # Usar últimos 6 períodos para tendência
        recent = volumes[-6:] if len(volumes) >= 6 else volumes
        
        # Calcular slope usando regressão linear simples
        x = np.arange(len(recent))
        y = np.array(recent)
        
        # Normalizar para evitar problemas de escala
        y_normalized = y / np.mean(y) if np.mean(y) > 0 else y
        
        # Coeficiente de correlação
        correlation = np.corrcoef(x, y_normalized)[0, 1] if len(x) > 1 else 0
        
        # Slope normalizado
        if len(x) > 1:
            slope = np.polyfit(x, y_normalized, 1)[0]
        else:
            slope = 0
        
        # Determinar direção e força
        if slope > 0.05 and correlation > 0.3:
            direction = "up"
            strength = min(abs(correlation), 1.0)
        elif slope < -0.05 and correlation < -0.3:
            direction = "down"
            strength = min(abs(correlation), 1.0)
        else:
            direction = "flat"
            strength = 0
        
        return {"direction": direction, "strength": strength, "slope": slope}
    
    def _trend_to_score(self, trend: Dict, price_change: float) -> float:
        """
        Converte tendência de volume para score.
        
        Volume subindo + preço subindo = muito bullish
        Volume subindo + preço caindo = possível reversão
        Volume caindo = menos interesse
        """
        direction = trend.get("direction", "flat")
        strength = trend.get("strength", 0)
        
        base_score = 50
        
        if direction == "up":
            base_score = 60 + strength * 20  # 60-80
            # Bônus se preço também está subindo
            if price_change > 0:
                base_score += min(10, price_change)
        elif direction == "down":
            base_score = 40 - strength * 15  # 25-40
        # flat = 50
        
        return self.clamp_score(base_score)
    
    def _relative_to_score(self, ratio: float) -> float:
        """
        Converte ratio (volume/média) para score.
        """
        if ratio >= 3:
            return 90  # 3x a média
        elif ratio >= 2:
            return 75 + (ratio - 2) * 15  # 75-90
        elif ratio >= 1.5:
            return 65 + (ratio - 1.5) * 20  # 65-75
        elif ratio >= 1:
            return 50 + (ratio - 1) * 30  # 50-65
        elif ratio >= 0.5:
            return 30 + (ratio - 0.5) * 40  # 30-50
        else:
            return max(15, ratio * 60)  # 0-30
    
    def _generate_reason(self, z_score: float, trend: Dict, ratio: float) -> str:
        """Gera explicação textual."""
        reasons = []
        
        if z_score >= self.Z_SCORE_THRESHOLD_EXTREME:
            reasons.append(f"Volume EXTREMO ({z_score:.1f} desvios)")
        elif z_score >= self.Z_SCORE_THRESHOLD_HIGH:
            reasons.append(f"Volume muito alto ({z_score:.1f} desvios)")
        elif z_score >= 1:
            reasons.append("Volume acima da média")
        elif z_score <= -2:
            reasons.append("Volume muito baixo")
        elif z_score <= -1:
            reasons.append("Volume abaixo da média")
        
        if ratio >= 2:
            reasons.append(f"{ratio:.1f}x a média")
        
        if trend["direction"] == "up":
            reasons.append("tendência de alta no volume")
        elif trend["direction"] == "down":
            reasons.append("tendência de queda no volume")
        
        return "; ".join(reasons) if reasons else "Volume dentro da normalidade"
