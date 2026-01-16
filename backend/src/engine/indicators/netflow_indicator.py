"""
Indicador de Netflow de Exchanges.

Analisa:
- Fluxo líquido (entrada - saída) de exchanges
- Tendência de acumulação/distribuição
- Comparação com média histórica

NOTA: Como Glassnode é pago, usamos dados estimados via whale transactions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import numpy as np

from .base_indicator import BaseIndicator


class NetflowIndicator(BaseIndicator):
    """
    Calcula score baseado em fluxo de exchanges.
    
    Sinais bullish (score alto):
    - Netflow negativo (mais saídas que entradas)
    - Whales retirando de exchanges
    - Tendência de acumulação em cold wallets
    
    Sinais bearish (score baixo):
    - Netflow positivo (mais entradas que saídas)
    - Whales depositando em exchanges (potencial venda)
    """
    
    # Pesos internos
    WEIGHT_NETFLOW = 0.45
    WEIGHT_TREND = 0.30
    WEIGHT_MAGNITUDE = 0.25
    
    def __init__(self, weight: float = 0.25):
        """
        Inicializa o indicador de netflow.
        
        Args:
            weight: Peso no score final (padrão 25%)
        """
        super().__init__(name="exchange_netflow", weight=weight)
    
    async def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calcula o score de netflow.
        
        Args:
            data: {
                "inflow_usd": float,  # Total entrando em exchanges
                "outflow_usd": float,  # Total saindo de exchanges
                "historical_netflows": List[float],  # Netflows históricos
                "total_supply": float,  # Supply total (opcional)
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
        inflow = data.get("inflow_usd", 0)
        outflow = data.get("outflow_usd", 0)
        historical = data.get("historical_netflows", [])
        total_supply = data.get("total_supply", 0)
        asset_symbol = data.get("asset_symbol", "UNKNOWN")
        
        # Netflow = Inflow - Outflow
        # Positivo = mais entrando (bearish)
        # Negativo = mais saindo (bullish)
        netflow = inflow - outflow
        total_flow = inflow + outflow
        
        # Se não há fluxo significativo
        if total_flow < 10000:  # Menos de $10k
            details = {
                "inflow_usd": inflow,
                "outflow_usd": outflow,
                "netflow_usd": netflow,
                "netflow_ratio": 0,
                "sub_scores": {
                    "netflow_score": 50,
                    "trend_score": 50,
                    "magnitude_score": 50,
                },
                "interpretation": "low_activity",
                "reason": "Fluxo de exchanges muito baixo"
            }
            self._update_state(50.0, data, details)
            return {"score": 50.0, "details": details}
        
        # Ratio de netflow (-1 a +1)
        netflow_ratio = netflow / total_flow if total_flow > 0 else 0
        
        # === SUB-SCORES ===
        
        # 1. Netflow Score (principal)
        netflow_score = self._netflow_to_score(netflow_ratio)
        
        # 2. Trend Score (tendência histórica)
        trend_score = self._calculate_trend_score(netflow, historical)
        
        # 3. Magnitude Score (tamanho relativo ao supply)
        magnitude_score = self._calculate_magnitude_score(abs(netflow), total_supply, total_flow)
        
        # === SCORE FINAL ===
        final_score = (
            netflow_score * self.WEIGHT_NETFLOW +
            trend_score * self.WEIGHT_TREND +
            magnitude_score * self.WEIGHT_MAGNITUDE
        )
        final_score = self.clamp_score(final_score)
        
        # Detalhes
        details = {
            "inflow_usd": inflow,
            "outflow_usd": outflow,
            "netflow_usd": netflow,
            "total_flow_usd": total_flow,
            "netflow_ratio": round(netflow_ratio, 4),
            "sub_scores": {
                "netflow_score": round(netflow_score, 2),
                "trend_score": round(trend_score, 2),
                "magnitude_score": round(magnitude_score, 2),
            },
            "interpretation": self._interpret_netflow(netflow_ratio),
            "reason": self._generate_reason(netflow, netflow_ratio, total_flow)
        }
        
        self._update_state(final_score, data, details)
        
        logger.debug(
            f"[{self.name}] {asset_symbol}: score={final_score:.1f}, "
            f"netflow=${netflow:,.0f}, ratio={netflow_ratio:.2%}"
        )
        
        return {"score": final_score, "details": details}
    
    def _netflow_to_score(self, ratio: float) -> float:
        """
        Converte ratio de netflow para score.
        
        ratio < 0: Saindo de exchanges (bullish) -> score alto
        ratio > 0: Entrando em exchanges (bearish) -> score baixo
        """
        # Inverter: netflow negativo = bullish = score alto
        # ratio -1 -> score 90
        # ratio 0 -> score 50
        # ratio +1 -> score 10
        
        score = 50 - (ratio * 40)
        return self.clamp_score(score)
    
    def _calculate_trend_score(self, current_netflow: float, historical: List[float]) -> float:
        """
        Calcula score baseado na tendência de netflows.
        """
        if len(historical) < 3:
            return 50.0
        
        # Adicionar atual ao histórico para análise
        all_flows = historical + [current_netflow]
        
        # Verificar se tendência é de saída (bullish)
        recent = all_flows[-5:] if len(all_flows) >= 5 else all_flows
        
        # Contar quantos são negativos (saídas)
        negative_count = sum(1 for f in recent if f < 0)
        negative_ratio = negative_count / len(recent)
        
        # Calcular tendência
        if len(recent) >= 3:
            # Regressão simples
            x = np.arange(len(recent))
            y = np.array(recent)
            slope = np.polyfit(x, y, 1)[0] if len(x) > 1 else 0
            
            # Slope negativo = tendência de saída = bullish
            if slope < -1000000:  # Forte tendência de saída
                trend_bonus = 20
            elif slope < 0:
                trend_bonus = 10
            elif slope > 1000000:  # Forte tendência de entrada
                trend_bonus = -20
            else:
                trend_bonus = -10
        else:
            trend_bonus = 0
        
        # Score base + tendência
        base_score = 30 + (negative_ratio * 40)  # 30-70 baseado em quantos são saídas
        final_score = base_score + trend_bonus
        
        return self.clamp_score(final_score)
    
    def _calculate_magnitude_score(self, abs_netflow: float, total_supply: float, total_flow: float) -> float:
        """
        Calcula score baseado na magnitude do fluxo.
        
        Fluxo grande = movimento significativo
        """
        # Se temos supply, calcular como % do supply
        if total_supply > 0:
            flow_percent = (total_flow / total_supply) * 100
            
            if flow_percent >= 1:  # 1% do supply
                return 85
            elif flow_percent >= 0.5:
                return 70 + (flow_percent - 0.5) * 30
            elif flow_percent >= 0.1:
                return 55 + (flow_percent - 0.1) * 37.5
            else:
                return 50 + flow_percent * 50
        
        # Fallback: usar valores absolutos
        if total_flow >= 100_000_000:  # $100M+
            return 85
        elif total_flow >= 50_000_000:  # $50M+
            return 70
        elif total_flow >= 10_000_000:  # $10M+
            return 60
        elif total_flow >= 1_000_000:  # $1M+
            return 55
        else:
            return 50
    
    def _interpret_netflow(self, ratio: float) -> str:
        """Interpreta o cenário de netflow."""
        if ratio <= -0.5:
            return "strong_accumulation"
        elif ratio <= -0.2:
            return "accumulation"
        elif ratio >= 0.5:
            return "strong_distribution"
        elif ratio >= 0.2:
            return "distribution"
        else:
            return "neutral"
    
    def _generate_reason(self, netflow: float, ratio: float, total_flow: float) -> str:
        """Gera explicação textual."""
        reasons = []
        
        if netflow < 0:
            reasons.append(f"${abs(netflow):,.0f} saindo de exchanges")
            if ratio <= -0.5:
                reasons.append("forte acumulação")
            elif ratio <= -0.2:
                reasons.append("acumulação moderada")
        elif netflow > 0:
            reasons.append(f"${netflow:,.0f} entrando em exchanges")
            if ratio >= 0.5:
                reasons.append("forte distribuição")
            elif ratio >= 0.2:
                reasons.append("distribuição moderada")
        
        if total_flow >= 50_000_000:
            reasons.append("volume de fluxo muito alto")
        elif total_flow >= 10_000_000:
            reasons.append("volume de fluxo significativo")
        
        return "; ".join(reasons) if reasons else "Fluxo de exchanges neutro"
