"""
Indicador de Open Interest (Derivativos).

Analisa:
- Variação de OI (Open Interest)
- OI vs Preço (divergências)
- Funding rate
- Long/Short ratio
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import numpy as np

from .base_indicator import BaseIndicator


class OpenInterestIndicator(BaseIndicator):
    """
    Calcula score baseado em métricas de derivativos.
    
    Sinais bullish (score alto):
    - OI subindo com preço subindo (novos longs entrando)
    - OI subindo com preço caindo (shorts abrindo - potencial squeeze)
    - Funding rate negativo (shorts pagando - potencial squeeze)
    
    Sinais neutros/bearish:
    - OI caindo (posições sendo fechadas)
    - OI estável (mercado lateral)
    """
    
    # Pesos internos
    WEIGHT_OI_CHANGE = 0.35
    WEIGHT_OI_PRICE_DIVERGENCE = 0.30
    WEIGHT_FUNDING = 0.20
    WEIGHT_RATIO = 0.15
    
    def __init__(self, weight: float = 0.15):
        """
        Inicializa o indicador de Open Interest.
        
        Args:
            weight: Peso no score final (padrão 15%)
        """
        super().__init__(name="oi_pressure", weight=weight)
    
    async def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calcula o score de pressão de OI.
        
        Args:
            data: {
                "current_oi": float,  # OI atual em USD
                "previous_oi": float,  # OI anterior (ex: 24h atrás)
                "historical_oi": List[float],  # OI histórico
                "price_change_percent": float,  # Mudança de preço
                "funding_rate": float,  # Taxa de funding (-0.01 a +0.01)
                "long_short_ratio": float,  # Ratio long/short
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
        # Extrair dados com valores padrão seguros
        current_oi = data.get("current_oi") or 0
        previous_oi = data.get("previous_oi") or 0
        historical_oi = data.get("historical_oi") or []
        price_change = data.get("price_change_percent")
        funding_rate = data.get("funding_rate")
        long_short_ratio = data.get("long_short_ratio")
        asset_symbol = data.get("asset_symbol", "UNKNOWN")
        
        # Garantir que valores numéricos não sejam None
        price_change = float(price_change) if price_change is not None else 0.0
        funding_rate = float(funding_rate) if funding_rate is not None else 0.0
        long_short_ratio = float(long_short_ratio) if long_short_ratio is not None else 1.0
        
        # Se não há dados de OI
        if current_oi == 0 and previous_oi == 0:
            details = {
                "current_oi": 0,
                "oi_change_percent": 0,
                "funding_rate": funding_rate,
                "long_short_ratio": long_short_ratio,
                "sub_scores": {
                    "oi_change_score": 50,
                    "divergence_score": 50,
                    "funding_score": 50,
                    "ratio_score": 50,
                },
                "reason": "Dados de OI não disponíveis"
            }
            self._update_state(50.0, data, details)
            return {"score": 50.0, "details": details}
        
        # Calcular mudança de OI
        if previous_oi > 0:
            oi_change_percent = ((current_oi - previous_oi) / previous_oi) * 100
        else:
            oi_change_percent = 0.0
        
        # === SUB-SCORES ===
        
        # 1. OI Change Score
        oi_change_score = self._oi_change_to_score(oi_change_percent)
        
        # 2. Divergence Score (OI vs Price)
        divergence_score = self._divergence_to_score(oi_change_percent, price_change)
        
        # 3. Funding Score
        funding_score = self._funding_to_score(funding_rate)
        
        # 4. Long/Short Ratio Score
        ratio_score = self._ratio_to_score(long_short_ratio)
        
        # === SCORE FINAL ===
        final_score = (
            oi_change_score * self.WEIGHT_OI_CHANGE +
            divergence_score * self.WEIGHT_OI_PRICE_DIVERGENCE +
            funding_score * self.WEIGHT_FUNDING +
            ratio_score * self.WEIGHT_RATIO
        )
        final_score = self.clamp_score(final_score)
        
        # Detalhes
        details = {
            "current_oi": current_oi,
            "previous_oi": previous_oi,
            "oi_change_percent": round(oi_change_percent, 2),
            "price_change_percent": price_change,
            "funding_rate": funding_rate,
            "long_short_ratio": long_short_ratio,
            "sub_scores": {
                "oi_change_score": round(oi_change_score, 2),
                "divergence_score": round(divergence_score, 2),
                "funding_score": round(funding_score, 2),
                "ratio_score": round(ratio_score, 2),
            },
            "interpretation": self._interpret_oi(oi_change_percent, price_change),
            "reason": self._generate_reason(oi_change_percent, price_change, funding_rate)
        }
        
        self._update_state(final_score, data, details)
        
        logger.debug(
            f"[{self.name}] {asset_symbol}: score={final_score:.1f}, "
            f"OI change={oi_change_percent:.1f}%, funding={funding_rate:.4f}"
        )
        
        return {"score": final_score, "details": details}
    
    def _oi_change_to_score(self, oi_change: float) -> float:
        """
        Converte mudança de OI para score.
        
        OI subindo = mais interesse/posições = potencial movimento
        OI caindo = posições fechando = menos pressão
        """
        # OI subindo é geralmente bullish (mais interesse)
        if oi_change >= 20:
            return 85.0
        elif oi_change >= 10:
            return 70.0 + (oi_change - 10) * 1.5
        elif oi_change >= 5:
            return 60.0 + (oi_change - 5) * 2
        elif oi_change >= 0:
            return 50.0 + oi_change * 2
        elif oi_change >= -5:
            return 50.0 + oi_change * 2  # 40-50
        elif oi_change >= -10:
            return 40.0 + (oi_change + 5) * 2  # 30-40
        else:
            return max(20.0, 30.0 + (oi_change + 10))
    
    def _divergence_to_score(self, oi_change: float, price_change: float) -> float:
        """
        Analisa divergência entre OI e preço.
        
        Cenários interessantes:
        - OI ↑ + Price ↑: Confirmação de alta (bullish)
        - OI ↑ + Price ↓: Shorts entrando (potencial squeeze = bullish)
        - OI ↓ + Price ↑: Short squeeze acontecendo (neutral/bullish)
        - OI ↓ + Price ↓: Longs liquidando (bearish)
        """
        if oi_change > 5 and price_change > 2:
            # OI e preço subindo = tendência confirmada
            return 75.0 + min(15.0, oi_change / 2)
        elif oi_change > 5 and price_change < -2:
            # OI subindo, preço caindo = shorts entrando = potencial squeeze
            return 70.0 + min(15.0, oi_change / 2)
        elif oi_change < -5 and price_change > 2:
            # OI caindo, preço subindo = short squeeze
            return 65.0
        elif oi_change < -5 and price_change < -2:
            # Tudo caindo = bearish
            return 30.0 - min(10.0, abs(oi_change) / 2)
        else:
            # Movimento normal
            return 50.0
    
    def _funding_to_score(self, funding_rate: float) -> float:
        """
        Converte funding rate para score.
        
        Funding negativo = shorts pagando = potencial squeeze = bullish
        Funding muito positivo = longs sobrecarregados = potencial correção
        """
        # Funding rate geralmente varia de -0.1% a +0.1% por 8h
        if funding_rate <= -0.0005:  # -0.05% ou menos
            # Shorts dominantes, potencial squeeze
            return 75.0 + min(15.0, abs(funding_rate) * 10000)
        elif funding_rate <= 0:
            # Levemente negativo
            return 60.0 + abs(funding_rate) * 5000
        elif funding_rate <= 0.0005:
            # Normal/levemente positivo
            return 50.0
        elif funding_rate <= 0.001:
            # Longs pagando
            return 45.0
        else:
            # Funding muito alto, mercado pode estar superaquecido
            return max(30.0, 45.0 - (funding_rate - 0.001) * 5000)
    
    def _ratio_to_score(self, long_short_ratio: float) -> float:
        """
        Converte long/short ratio para score.
        
        Ratio < 1: Mais shorts = potencial squeeze = bullish
        Ratio > 1: Mais longs = mercado otimista
        Ratio muito alto: Pode estar sobrecomprado
        """
        if long_short_ratio < 0.8:
            # Muitos shorts, potencial squeeze
            return 75.0 + min(15.0, (1 - long_short_ratio) * 30)
        elif long_short_ratio < 1.0:
            # Levemente mais shorts
            return 60.0 + (1 - long_short_ratio) * 50
        elif long_short_ratio < 1.2:
            # Equilibrado/levemente mais longs
            return 50.0 + (long_short_ratio - 1) * 25
        elif long_short_ratio < 1.5:
            # Mais longs
            return 55.0
        else:
            # Muitos longs, pode estar sobrecomprado
            return max(35.0, 55.0 - (long_short_ratio - 1.5) * 20)
    
    def _interpret_oi(self, oi_change: float, price_change: float) -> str:
        """Interpreta o cenário de OI."""
        if oi_change > 5 and price_change > 2:
            return "bullish_continuation"
        elif oi_change > 5 and price_change < -2:
            return "potential_short_squeeze"
        elif oi_change < -5 and price_change > 2:
            return "short_squeeze_in_progress"
        elif oi_change < -5 and price_change < -2:
            return "long_liquidation"
        elif oi_change > 0:
            return "building_positions"
        elif oi_change < 0:
            return "closing_positions"
        else:
            return "neutral"
    
    def _generate_reason(self, oi_change: float, price_change: float, funding: float) -> str:
        """Gera explicação textual."""
        reasons = []
        
        if oi_change > 10:
            reasons.append(f"OI subindo forte (+{oi_change:.1f}%)")
        elif oi_change > 5:
            reasons.append(f"OI em alta (+{oi_change:.1f}%)")
        elif oi_change < -10:
            reasons.append(f"OI caindo forte ({oi_change:.1f}%)")
        elif oi_change < -5:
            reasons.append(f"OI em queda ({oi_change:.1f}%)")
        
        if oi_change > 5 and price_change < -2:
            reasons.append("possível short squeeze à vista")
        elif oi_change < -5 and price_change > 2:
            reasons.append("squeeze em andamento")
        
        if funding < -0.0003:
            reasons.append("funding negativo (shorts dominantes)")
        elif funding > 0.0007:
            reasons.append("funding elevado (cautela)")
        
        return "; ".join(reasons) if reasons else "Métricas de derivativos normais"
